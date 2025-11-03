import os
from spotipy.oauth2 import SpotifyOAuth


def get_spotify_oauth():
    """Creates and returns a SpotifyOAuth object."""
    return SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope="user-read-playback-state user-modify-playback-state playlist-read-private user-read-currently-playing",
    )

def get_authorize_url(oauth):
    """Gets the authorization URL."""
    return oauth.get_authorize_url()

def get_access_token(oauth, code):
    """Gets the access token."""
    return oauth.get_access_token(code)
