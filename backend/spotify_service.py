import spotipy
import os
from spotipy.oauth2 import SpotifyOAuth

# This service file contains the core logic for interacting with the Spotify API.
# It is used by the routers to expose functionality via HTTP endpoints and by the agent flow.

# --- Authentication Functions ---

def get_spotify_oauth():
    """Creates and returns a SpotifyOAuth object."""
    return SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope="streaming user-read-email user-read-private user-read-playback-state user-modify-playback-state user-read-currently-playing",
        cache_handler=None
    )

def get_access_token(code: str) -> dict:
    """Gets the access token from the authorization code."""
    oauth = get_spotify_oauth()
    return oauth.get_access_token(code)

# --- Data Fetching and Preprocessing ---

def _preprocess_user_context(context: dict) -> dict:
    processed_context = {}

    # Process top tracks
    if context.get("top_tracks"):
        processed_context["top_tracks"] = [
            {
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "uri": track["uri"],
            }
            for track in context["top_tracks"]
        ]

    # Process top artists
    if context.get("top_artists"):
        processed_context["top_artists"] = [
            {
                "name": artist["name"],
                "genres": artist["genres"],
            }
            for artist in context["top_artists"]
        ]

    # Process recently played
    if context.get("recently_played"):
        processed_context["recently_played"] = [
            {
                "name": item["track"]["name"],
                "artist": item["track"]["artists"][0]["name"],
                "uri": item["track"]["uri"],
            }
            for item in context["recently_played"]
        ]

    return processed_context

def get_user_context(token_info: dict):
    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        raw_context = {
            "top_tracks": sp.current_user_top_tracks(limit=20, time_range="medium_term")["items"],
            "top_artists": sp.current_user_top_artists(limit=20, time_range="medium_term")["items"],
            "recently_played": sp.current_user_recently_played(limit=20)["items"],
        }
        return _preprocess_user_context(raw_context)
    except Exception as e:
        return {"error": f"Error fetching user context: {e}"}
    
def add_to_queue(token_info: dict, song_uri: str):
    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        sp.add_to_queue(song_uri)
        return {"message": f"Added {song_uri} to queue."}
    except Exception as e:
        return {"error": f"Error adding to queue: {e}"}

def start_playback(token_info: dict):
    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        sp.start_playback()
        return {"message": "Playback started."}
    except Exception as e:
        return {"error": f"Error starting playback: {e}"}

def pause_playback(token_info: dict):
    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        sp.pause_playback()
        return {"message": "Playback paused."}
    except Exception as e:
        return {"error": f"Error pausing playback: {e}"}

def next_track(token_info: dict):
    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        sp.next_track()
        return {"message": "Skipped to next track."}
    except Exception as e:
        return {"error": f"Error skipping track: {e}"}

def get_current_playback(token_info: dict):
    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        current_playback = sp.current_playback()
        if current_playback:
            return {"current_playback": current_playback}
        else:
            return {"message": "No track currently playing."}
    except Exception as e:
        return {"error": f"Error fetching current playback: {e}"}

def search_track(token_info: dict, query: str):
    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        results = sp.search(q=query, type="track", limit=10)
        return {"results": results["tracks"]["items"]}
    except Exception as e:
        return {"error": f"Error searching track: {e}"}

def get_current_queue(token_info: dict):
    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        queue = sp.queue()
        return queue
    except Exception as e:
        return {"error": f"Error fetching queue: {e}"}

def stop_playback(token_info: dict):
    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        sp.pause_playback()
        return {"message": "Playback stopped."}
    except Exception as e:
        return {"error": f"Error stopping playback: {e}"}

def create_playlist_from_queue(token_info: dict, playlist_name: str):
    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        user_id = sp.current_user()["id"]
        queue_items = sp.queue()["queue"]
        track_uris = [item["uri"] for item in queue_items]

        if not track_uris:
            return {"message": "Queue is empty, no playlist created."}

        playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False)
        sp.playlist_add_items(playlist_id=playlist["id"], items=track_uris)
        return {"message": f"Playlist '{playlist_name}' created with {len(track_uris)} songs."}
    except Exception as e:
        return {"error": f"Error creating playlist from queue: {e}"}

def add_track_to_likes(token_info: dict, track_uri: str):
    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        sp.current_user_saved_tracks_add([track_uri])
        return {"message": f"Added {track_uri} to liked songs."}
    except Exception as e:
        return {"error": f"Error adding track to liked songs: {e}"}

def get_user_playlists(token_info: dict):
    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        playlists = sp.current_user_playlists(limit=50) # Limit to 50 for now
        return {"playlists": playlists["items"]}
    except Exception as e:
        return {"error": f"Error fetching user playlists: {e}"}

def previous_track(token_info: dict):
    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        sp.previous_track()
        return {"message": "Skipped to previous track."}
    except Exception as e:
        return {"error": f"Error skipping to previous track: {e}"}
