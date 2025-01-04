import os
import time
import requests


class SpotifyTokenGenerator:
    """
    Class that can generate and re-generate a Spotify token.
    The token is regenerated every 59 minutes as it expires after an hour.
    """
    def __init__(self):
        self.url = "https://accounts.spotify.com/api/token"
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self.data = {"grant_type": "client_credentials"}

        self.client_id = os.environ.get("SPOTIFY_CLIENT_ID")
        self.client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
        self.auth = (self.client_id, self.client_secret)

        self.token_lifespan = 59 * 60
        self.token_init = time.time()
        self.token = None

    def _get_new_token(self) -> str:
        """
        Get an access token from Spotify API.
        """
        response = requests.post(self.url, headers=self.headers, data=self.data, auth=self.auth)
        response.raise_for_status()
        token = response.json()["access_token"]

        self.token_init = time.time()
        self.token = token
        return token

    def get_token(self) -> str:
        """
        Sets the new access token if it has not been set in the last 59 minutes.
        """
        current_time = time.time()

        # Check if the token is missing or expired
        if not self.token or (current_time - self.token_init) >= self.token_lifespan:
            self._get_new_token()  # Get a new token

        return self.token
