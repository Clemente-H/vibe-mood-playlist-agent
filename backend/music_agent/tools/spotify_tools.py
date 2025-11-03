import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from google.adk.tools import FunctionTool, ToolContext

def get_spotify_oauth():
    """Creates and returns a SpotifyOAuth object."""
    return SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope="user-read-playback-state user-modify-playback-state playlist-read-private user-read-currently-playing",
    )

def get_access_token(code: str) -> dict:
    """Gets the access token from the authorization code."""
    oauth = get_spotify_oauth()
    return oauth.get_access_token(code)

def search_track(query: str, tool_context: ToolContext) -> str:
    """Searches for a track on Spotify and returns its URI."""
    token_info = tool_context.get("token_info")
    if not token_info:
        return "Error: Could not find token_info in the tool context."

    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        results = sp.search(q=query, type="track", limit=1)
        if results["tracks"]["items"]:
            track_uri = results["tracks"]["items"][0]["uri"]
            return track_uri
        else:
            return "Could not find any tracks for the given query."
    except Exception as e:
        return f"Error interacting with Spotify: {e}"

def add_to_queue(track_uri: str, tool_context: ToolContext):
    """Adds a track to the user's queue."""
    token_info = tool_context.get("token_info")
    if not token_info:
        return "Error: Could not find token_info in the tool context."

    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        sp.add_to_queue(track_uri)
        return f"Added {track_uri} to the queue."
    except Exception as e:
        return f"Error interacting with Spotify: {e}"

spotify_tools = [
    FunctionTool(search_track),
    FunctionTool(add_to_queue),
]
