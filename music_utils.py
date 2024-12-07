"""
Standalone functions that do musical calculations
"""
import os
import hashlib
import requests
import acoustid
import musicbrainzngs
from decorators import robust
from config import VibesterConfig
from typing import Optional, Dict


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
    Decides if a single file is musical based on the extension
    """
    for extension in VibesterConfig.supported_formats:
        if filename.endswith(extension):
            return True
    return False


def calculate_hash(input_string: str, hash_length: int = VibesterConfig.hash_length) -> str:
    """
    Calculates the hash of a given string
    Used when encoding music into a QR code
    """
    md5_hash = hashlib.md5(input_string.encode())
    return md5_hash.hexdigest()[:hash_length]


@robust
def query_acoustid(file_path: str) -> Optional[str]:
    """
    Uses acoustid to fingerprint a single music file and returns its recording ID
    """
    api_key_acoustid = os.getenv("API_KEY_ACOUSTID")
    results = acoustid.match(api_key_acoustid, file_path)
    for score, recording_id, title, artist in results:
        if score > VibesterConfig.fingerprint_conf_threshold:
            return recording_id
    return None


@robust
def query_musicbrainz(recording_id: str) -> Dict[str, Optional[str]]:
    """
    Queries the MusicBrainz API for music recordings based on the recording ID
    """
    result = musicbrainzngs.get_recording_by_id(recording_id, includes=["artists", "releases", "tags"])
    recording = result["recording"]

    title = recording["title"]

    artist = ", ".join(artist["artist"]["name"] for artist in recording["artist-credit"])

    year = recording["release-list"][0].get("date", "").split("-")[0]

    tags = []
    for tag in recording["artist-credit"][0]["artist"]["tag-list"]:
        tags.append(tag.get("name", ""))
    genre = ";".join(tags)

    return {"title": title, "artist": artist, "year": year, "genre": genre}


@robust
def query_deezer(title: str, artist: str) -> Optional[Dict[str, str]]:
    """
    Queries the Deezer API to find the metadata of a song, including its release year.
    """
    # Search for track
    search_url = "https://api.deezer.com/search"
    params = {"q": f"track:\"{title}\" artist:\"{artist}\""}
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
def get_metadata(file_path: str) -> Optional[Dict[str, str]]:
    """
    Creates a fingerprint from a musical track and creates its track ID.
    """
    recording_id = query_acoustid(file_path)

    if recording_id:
        metadata = query_musicbrainz(recording_id)
    else:
        return None

    if metadata["title"] and metadata["artist"]:
        year = query_deezer(title=metadata["title"], artist=metadata["artist"])
        if year:
            metadata["year"] = year

    print(f"Successfully processed: {metadata}")
    return metadata


