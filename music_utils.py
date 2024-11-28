"""
Standalone functions that do musical calculations
"""
import os
import hashlib
import acoustid
import musicbrainzngs
from typing import Optional, Dict



def is_music_file(filename: str) -> bool:
    """
    Decides if a single file is musical based on the extension
    """
    for extension in [".mp3", ".mp4", ".ogg", ".wav", ".wma", ".m4a"]:
        if filename.endswith(extension):
            return True
    return False


def calculate_md5(input_string: str) -> str:
    """
    Calculates the MD5 hash of a given string
    Used when encoding music into a QR code
    """
    md5_hash = hashlib.md5(input_string.encode())
    return md5_hash.hexdigest()


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


def get_musicbrainz_metadata(recording_id: str) -> Optional[Dict[str, str]]:
    """
    Downloads metadata like title, artist, year, genre from the musicbrainz database
    """
    try:
        # Query MusicBrainz for recording details
        recording = musicbrainzngs.get_recording_by_id(recording_id, includes=["artists", "releases", "tags"])

        # Extract title
        try:
            title = recording["recording"]["title"]
        except KeyError:
            print(f"Unable to get title from recording metadata: {recording}")
            title = ""

        # Extract artist
        try:
            artist = ", ".join(artist["artist"]["name"] for artist in recording["recording"]["artist-credit"])
        except KeyError:
            print(f"Unable to get artist from recording metadata: {recording}")
            artist = ""

        # Extract year
        try:
            year = recording["recording"]["release-list"][0].get("date", "").split("-")[0]
        except KeyError:
            print(f"Unable to get year from recording metadata: {recording}")
            year = ""

        # Extract genre tags
        try:
            tags = []
            for tag in recording["recording"]["artist-credit"][0]["artist"]["tag-list"]:
                tags.append(tag.get("name", ""))
            genre = ";".join(tags)
        except KeyError:
            print(f"Unable to get genre from recording metadata: {recording}")
            genre = ""

        return {"title": title, "artist": artist, "year": year, "genre": genre}

    except musicbrainzngs.WebServiceError as e:
        print(f"MusicBrainz error: {e}")
        return None


def get_metadata(file_path: str) -> Optional[Dict[str, str]]:
    """
    Creates a fingerprint from a musical track and creates its track ID.
    """
    try:
        # Match the audio file to an AcoustID
        api_key_acoustid = os.getenv("API_KEY_ACOUSTID")
        results = acoustid.match(api_key_acoustid, file_path)
        for score, recording_id, title, artist in results:
            print(f"Matched AcoustID: Score {score:.2f}, Recording ID {recording_id}")

            # Fetch detailed metadata from MusicBrainz
            return get_musicbrainz_metadata(recording_id)

    except acoustid.AcoustidError as e:
        print(f"AcoustID error: {e}")
        return None

