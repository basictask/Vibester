import os
import re
import time
import hashlib
import requests
import acoustid
import musicbrainzngs
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from decorators import robust
from config import VibesterConfig
from typing import Optional, Dict, Union
from pages.generate.spotify_token import SpotifyTokenGenerator

spotify_token_generator = SpotifyTokenGenerator()


def setup_musicbrainz_client() -> None:
    """
    Configures the user agent for the MusicBrainz client.
    The data is read from the .env file. Please contact Daniel for this.
    """
    musicbrainzngs.set_useragent(
        app=os.getenv("APP_NAME"),
        version=os.getenv("APP_VERSION"),
        contact=os.getenv("APP_CONTACT"),
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
        year_mb = metadata.get("year", None)
        year_sp = query_spotify(title=metadata["title"], artist=metadata["artist"])
        year_dz = query_deezer(title=metadata["title"], artist=metadata["artist"])
        year = find_smallest_year(year_mb, year_dz, year_sp)
        if year:
            metadata["year"] = year
    else:
        print(f"Unsuccessful song ID for file: {filepath}")
        return dict()

    metadata["year"] = infer_year(s=str(metadata["year"]))

    print(f"{','.join([str(metadata[x]) for x in metadata.keys()])}")
    return metadata
