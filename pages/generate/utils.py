import os
import re
import time
import hashlib
import requests
import acoustid
import pandas as pd
import discogs_client
import musicbrainzngs
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from decorators import robust
from config import VibesterConfig
from mutagen.easyid3 import EasyID3
from pages.play.utils import find_file
from typing import Optional, Dict, Union
from pages.generate.spotify_token import SpotifyTokenGenerator

spotify_token_generator = SpotifyTokenGenerator()
discogs_client_inst = discogs_client.Client(
    f"{os.getenv('APP_NAME')}/{os.getenv('APP_VERSION')}", user_token=os.getenv("API_KEY_DISCOGS")
)


def is_music_file(filename: str) -> bool:
    """
    Decides if a single file is musical based on the extension.
    """
    for extension in VibesterConfig.supported_formats:
        if filename.endswith(extension):
            return True
    return False


def calculate_hash(input_string: str, hash_length: int = VibesterConfig.hash_length) -> str:
    """
    Calculates the hash of a given string.
    Used when encoding music into a QR code.
    """
    safe_string = os.fsdecode(input_string).encode("utf-8", errors="replace").decode("utf-8")
    md5_hash = hashlib.md5(safe_string.encode())  # Hash the UTF-8 safe filename
    return md5_hash.hexdigest()[:hash_length]


def infer_year(s: str) -> int | None:
    """
    Takes a string and returns the first integer of that string if any.
    """
    match = re.search(r'\d+', s)
    return int(match.group()) if match else None


def find_smallest_year(*args: Union[str, None]) -> Optional[int]:
    """
    Determine the smallest year from a list of arguments. Return None if no valid years are found.
    """
    valid_years = [int(arg) for arg in args if isinstance(arg, str) and arg.isdigit()]
    return min(valid_years, default=None)


@robust
def get_metadata_from_file(filepath: str) -> Dict[str, str]:
    """
    Extracts the metadata embedded into a mp3 file if possible.
    """
    audio = MP3(filepath, ID3=ID3)
    metadata = {
        "artist": str(audio.tags.get("TPE1").text[0]) if "TPE1" in audio.tags else None,  # Artist
        "title": str(audio.tags.get("TIT2").text[0]) if "TIT2" in audio.tags else None,  # Title
        "year": str(audio.tags.get("TDRC").text[0]) if "TDRC" in audio.tags else None,  # Year
    }
    return metadata


@robust
def get_recording_id(filepath: str) -> Optional[str]:
    """
    Uses acoustid to fingerprint a single music file and returns its recording ID.
    """
    api_key_acoustid = os.getenv("API_KEY_ACOUSTID")
    results = acoustid.match(api_key_acoustid, filepath)
    for score, recording_id, title, artist in results:
        if score > VibesterConfig.fingerprint_conf_threshold:
            return recording_id
    return None


@robust
def query_musicbrainz(recording_id: str) -> Dict[str, Optional[str]]:
    """
    Queries the MusicBrainz API for music recordings based on the recording ID.
    """
    result = musicbrainzngs.get_recording_by_id(recording_id, includes=["artists", "releases", "tags"])
    recording = result["recording"]

    # Get the title of the track
    try:
        title = recording["title"]
    except (KeyError, TypeError):
        title = ""

    # Get the artist of the track
    artists = []
    for artist in recording["artist-credit"]:
        try:
            artists.append(artist["artist"]["name"])
        except (KeyError, TypeError):
            continue
    artists = ", ".join(artists)

    # Get the year for the track
    try:
        year = recording["release-list"][0].get("date", "").split("-")[0]
    except (KeyError, TypeError):
        year = ""

    # Get the genre of the artist
    try:
        if "tag-list" in recording["artist-credit"][0]["artist"]:
            tags = []
            for tag in recording["artist-credit"][0]["artist"]["tag-list"]:
                tags.append(tag.get("name", ""))
            genre = ";".join(tags)
        elif "disambiguation" in recording["artist-credit"][0]["artist"]:
            genre = recording["artist-credit"][0]["artist"]["disambiguation"]
        else:
            genre = ""
    except (KeyError, TypeError):
        genre = ""

    time.sleep(0.34)  # At most 3 requests per second
    return {"title": title, "artist": artists, "year": year, "genre": genre}


@robust
def query_deezer(title: str, artist: str) -> Optional[Dict[str, str]]:
    """
    Queries the Deezer API to find the metadata of a song, including its release year.
    """
    # Search for track
    search_url = "https://api.deezer.com/search"
    params = {"q": f"track:\"{title}\" artist:\"{artist}\"".replace("?", "")}
    response = requests.get(search_url, params=params)
    response.raise_for_status()
    results = response.json()

    if not results["data"]:
        return None  # No results found

    # Extract track and album details
    track = results["data"][0]
    track_metadata = {
        "artist": track["artist"]["name"],
        "title": track["title"],
        "year": None,
        "album": track["album"]["title"],
        "album_id": track["album"]["id"],
    }

    # Fetch album details for the release year
    album_url = f"https://api.deezer.com/album/{track_metadata['album_id']}"
    album_response = requests.get(album_url)
    album_response.raise_for_status()
    album_data = album_response.json()

    # Add release year to the metadata
    if "release_date" in album_data:
        track_metadata["year"] = album_data["release_date"].split("-")[0]

    return track_metadata["year"]


@robust
def query_spotify(title: str, artist: str) -> Optional[str]:
    """
    Search for a song on Spotify.
    """
    url = "https://api.spotify.com/v1/search"
    token = spotify_token_generator.get_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": f"track:{title} artist:{artist}", "type": "track", "limit": 1}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    tracks = response.json().get("tracks", {}).get("items", [])

    if tracks:
        track = tracks[0]
        year = track["album"]["release_date"].split("-")[0]
        return year
    return None


def get_song_release_date(title: str, artist: str) -> Optional[str]:
    """
    Search for the release date of a song on Discogs.
    """
    # Search for the artist and track title.
    search_results = discogs_client_inst.search(title, artist=artist, type='release')

    # Handle no results found.
    if not search_results:
        print(f"No Discogs release found for '{title}' by '{artist}'.")
        return None

    # Iterate through the results and find the matching release.
    for release in search_results:
        if release.title.lower() == title.lower() and release.artists[0].name.lower() == artist.lower():
            return release.year

    print(f"Could not find an exact Discogs match for '{title}' by '{artist}'.")
    return None


@robust
def get_artist_from_filepath(filepath: str) -> Optional[str]:
    """
    Gets the artist name from a file path.
    Supposes that the file name is of the structure "artist - title.mp3".
    """
    filename = os.path.basename(filepath)
    match = re.match(r"^(.*?) - ", filename)
    return match.group(1) if match else None


@robust
def get_title_from_filepath(filepath: str) -> Optional[str]:
    """
    Gets the title from a file path.
    Supposes that the file name is of the structure "artist - title.mp3".
    """
    filename = os.path.basename(filepath)
    for fmt in VibesterConfig.supported_formats:
        if filename.endswith(fmt):
            filename = filename[:-len(fmt)]
            return filename.split(" - ", 1)[1]  # Extract the part after " - "
    return None


@robust
def get_metadata(filepath: str) -> Dict[str, str]:
    """
    Creates a fingerprint from a musical track and creates its track ID.
    """
    metadata = get_metadata_from_file(filepath=filepath)  # Get metadata from IDv3 tags

    if metadata["artist"] and metadata["title"] and metadata["year"]:  # Everything encoded in IDv3 tags
        metadata["year"] = infer_year(metadata["year"])
        print(f"{','.join([str(metadata[x]) for x in metadata.keys()])}")
        return metadata

    if not metadata["artist"] or not metadata["title"]:  # Tags not encoded - fingerprinting
        recording_id = get_recording_id(filepath=filepath)
        if recording_id:
            metadata = query_musicbrainz(recording_id=recording_id)
        else:
            metadata["artist"] = get_artist_from_filepath(filepath)
            metadata["title"] = get_title_from_filepath(filepath)

    if metadata["title"] and metadata["artist"]:  # Tags found by fingerprinting - query year
        year_mb, year_sp, year_dz, year_dc = None, None, None, None

        if "musicbrainz" in VibesterConfig.metadata_sources:
            year_mb = metadata.get("year", None)

        if "spotify" in VibesterConfig.metadata_sources:
            year_sp = query_spotify(title=metadata["title"], artist=metadata["artist"])

        if "deezer" in VibesterConfig.metadata_sources:
            year_dz = query_deezer(title=metadata["title"], artist=metadata["artist"])

        if "discogs" in VibesterConfig.metadata_sources:
            year_dc = query_deezer(title=metadata["title"], artist=metadata["artist"])

        year = find_smallest_year(year_mb, year_dz, year_sp, year_dc)

        if year:
            metadata["year"] = year
    else:
        print(f"Unsuccessful song ID for file: {filepath}")
        return dict()

    metadata["year"] = infer_year(s=str(metadata["year"]))

    print(f"{','.join([str(metadata[x]) for x in metadata.keys()])}")
    return metadata


@robust
def write_id3_tags(filepath: str, artist: str, title: str, year: str) -> None:
    """
    Writes ID3 tags to an MP3 file.
    """
    if not artist or not title or not year:  # Only write if all 3 necessary tags are present
        return None

    tags = EasyID3(filepath)
    tags["artist"] = artist
    tags["title"] = title
    tags["date"] = str(year)
    tags.save()
    print(f"Tags updated successfully for {filepath}.")


@robust
def has_required_tags(filepath: str) -> bool:
    """
    Checks if an MP3 file contains the tags artist, title, and release date.
    """
    try:
        # Load the MP3 file with EasyID3
        audio = EasyID3(filepath)
        required_tags = ["artist", "title", "date"]  # EasyID3 tags
        return all(tag in audio for tag in required_tags)
    except Exception as e:
        print(f"Error while reading tags from {filepath}:\n{e}")
        return False


def write_id3_tags_batch(df: pd.DataFrame) -> None:
    """
    Writes ID3 tags to a DataFrame of MP3 files.
    The dataframe must have columns ["filename", "artist", "title", "year"].
    """
    if df.empty or len(df) == 0:
        return None

    assert "filename" in df.columns, "Batch MP3 tag write error, column 'filename' not found."
    assert "artist" in df.columns, "Batch MP3 tag write error, column 'artist' not found."
    assert "title" in df.columns, "Batch MP3 tag write error, column 'title' not found."
    assert "year" in df.columns, "Batch MP3 tag write error, column 'year' not found."

    for i in df.index:
        if (
            df.loc[i, "filename"] is not None
            and df.loc[i, "artist"] is not None
            and df.loc[i, "title"] is not None
            and df.loc[i, "year"] is not None
        ):
            filepath = find_file(root_dir=VibesterConfig.path_music, filename=df.loc[i, "filename"])
            if not has_required_tags(filepath=filepath):
                write_id3_tags(  # Save ID3 tags from the table to the MP3 file
                    filepath=filepath,
                    artist=df.loc[i, "artist"],
                    title=df.loc[i, "title"],
                    year=df.loc[i, "year"],
                )


if __name__ == "__main__":
    # This can be used as an automtic tagger
    # Usage: choose a target folder, and it will be traversed recursively. Music inside the folder will be tagged if
    # it is missing using fingerprinting then API queries.
    target_dir = "C:\\Users\\danie\\Music\\Hungarian"
    for root, _, files in os.walk(target_dir):  # Traverse target folder recursively
        for fname in files:
            filepath_tag = os.path.abspath(str(os.path.join(root, fname)))
            metadata_query = get_metadata(filepath=filepath_tag)
            write_id3_tags(
                filepath=filepath_tag,
                artist=metadata_query["artist"],
                title=metadata_query["title"],
                year=metadata_query["year"]
            )
