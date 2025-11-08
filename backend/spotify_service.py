import spotipy
import os
import time
from spotipy.oauth2 import SpotifyOAuth

# This service file contains the core logic for interacting with the
# Spotify API. It is used by the routers to expose functionality via
# HTTP endpoints and by the agent flow.

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
    token_info = oauth.get_access_token(code)
    # Manually add expires_at if it's not there, Spotipy usually adds it.
    if 'expires_at' not in token_info:
        token_info['expires_at'] = int(time.time()) + token_info['expires_in']
    return token_info


def refresh_token_if_needed(token_info: dict) -> dict:
    """
    Checks if the token is about to expire and refreshes it if necessary.
    Returns the (potentially updated) token_info.
    """
    if not token_info:
        return None

    # Refresh if the token has less than 60 seconds left
    if token_info.get('expires_at', 0) < time.time() + 60:
        try:
            oauth = get_spotify_oauth()
            new_token_info = oauth.refresh_access_token(token_info['refresh_token'])
            # Manually add expires_at if it's not there
            if 'expires_at' not in new_token_info:
                new_token_info['expires_at'] = int(time.time()) + new_token_info['expires_in']
            print("--- Spotify token refreshed successfully ---")
            return new_token_info
        except Exception as e:
            print(f"--- Error refreshing Spotify token: {e} ---")
            # Could not refresh, return original token to let it fail downstream
            return token_info
            
    return token_info


# --- Data Fetching and Preprocessing ---


def _fetch_playlist_tracks(sp: spotipy.Spotify, playlist_id: str, limit: int = 50) -> list:
    """
    Fetches tracks from a specific playlist.
    
    Args:
        sp: Spotify client
        playlist_id: ID of the playlist
        limit: Maximum number of tracks to fetch
    
    Returns:
        List of track dictionaries with name, artist, uri
    """
    try:
        tracks = sp.playlist_tracks(playlist_id, limit=limit)["items"]
        return [
            {
                "name": item["track"]["name"],
                "artist": item["track"]["artists"][0]["name"],
                "uri": item["track"]["uri"]
            }
            for item in tracks
            if item["track"]  # Skip null tracks
        ]
    except Exception as e:
        print(f"Warning: Could not fetch tracks for playlist {playlist_id}: {e}")
        return []


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

    # Process playlists (tracks already fetched and formatted)
    if context.get("playlists"):
        processed_context["playlists"] = [
            {
                "name": playlist["name"],
                "id": playlist["id"],
                "total_tracks": playlist["tracks"]["total"],
                "public": playlist.get("public", False),
                "owner": playlist["owner"]["display_name"],
                "tracks": playlist["tracks"].get("items", [])
            }
            for playlist in context["playlists"]
        ]

    # Extract top genres from top artists
    if context.get("top_artists"):
        all_genres = []
        for artist in context["top_artists"]:
            all_genres.extend(artist.get("genres", []))
        # Count genre frequency
        from collections import Counter
        genre_counts = Counter(all_genres)
        processed_context["top_genres"] = [
            genre for genre, count in genre_counts.most_common(10)
        ]

    return processed_context


def get_user_context(token_info: dict):
    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        # Fetch user's playlists
        playlists = sp.current_user_playlists(limit=50)["items"]
        
        # Select max 10 random playlists
        import random
        if len(playlists) > 10:
            playlists = random.sample(playlists, 10)
        
        # Enrich each playlist with its tracks (30 per playlist)
        for playlist in playlists:
            if playlist["tracks"]["total"] > 0:
                playlist["tracks"]["items"] = _fetch_playlist_tracks(
                    sp,
                    playlist["id"],
                    limit=30  # Changed to 30
                )
            else:
                playlist["tracks"]["items"] = []
        
        raw_context = {
            "top_tracks": sp.current_user_top_tracks(
                limit=20,
                time_range="medium_term"
            )["items"],
            "top_artists": sp.current_user_top_artists(
                limit=20,
                time_range="medium_term"
            )["items"],
            "recently_played": sp.current_user_recently_played(
                limit=20
            )["items"],
            "playlists": playlists,
        }
        
        # Process the context (no API calls in preprocessing)
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
    

def start_playback(token_info: dict, uri: str, device_id: str | None = None):
    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        sp.start_playback()
        return {"message": "Playback started."}
    except Exception as e:
        return {"error": f"Error starting playback: {e}"}
    
    
def start_playback_with_uris(token_info: dict, uris: list[str], device_id: str | None = None):
    """
    Reemplaza la playback queue con 'uris' y comienza a reproducir desde la primera.
    """
    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        sp.start_playback(device_id=device_id, uris=uris)
        return {"message": "Playback started.", "uris": uris}
    except Exception as e:
        return {"error": f"Error starting playback with uris: {e}"}


def start_playback_from_context(token_info: dict, context_uri: str, offset_uri: str | None = None, device_id: str | None = None):
    """
    Inicia reproducción en un contexto (playlist/álbum) y opcionalmente arrancando en 'offset_uri'.
    """
    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        offset = {"uri": offset_uri} if offset_uri else None
        sp.start_playback(device_id=device_id, context_uri=context_uri, offset=offset)
        return {"message": "Playback started from context.", "context_uri": context_uri, "offset_uri": offset_uri}
    except Exception as e:
        return {"error": f"Error starting playback from context: {e}"}
    


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

        playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=False
        )
        sp.playlist_add_items(playlist_id=playlist["id"], items=track_uris)
        msg = (
            f"Playlist '{playlist_name}' created with "
            f"{len(track_uris)} songs."
        )
        return {"message": msg}
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
        # Limit to 50 for now
        playlists = sp.current_user_playlists(limit=50)
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


def transfer_playback(token_info: dict, device_id: str):
    """Transfers playback to a new device and ensures playback starts."""
    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        sp.transfer_playback(device_id=device_id, force_play=True)
        return {"message": f"Playback transferred to device {device_id}."}
    except Exception as e:
        return {"error": f"Error transferring playback: {e}"}


def validate_track_uri(token_info: dict, track_uri: str) -> dict:
    """
    Validates if a Spotify track URI exists and is accessible.
    
    Args:
        token_info: Spotify authentication token
        track_uri: Spotify track URI (spotify:track:XXXXX)
    
    Returns:
        dict with validation result:
        - valid: bool
        - track_info: dict with track details if valid
        - error: str if invalid
    """
    sp = spotipy.Spotify(auth=token_info["access_token"])
    
    try:
        # Check URI format
        if not track_uri or not track_uri.startswith("spotify:track:"):
            return {
                "valid": False,
                "error": "Invalid URI format"
            }
        
        # Extract track ID
        track_id = track_uri.split(":")[-1]
        
        # Try to fetch track info from Spotify
        track_info = sp.track(track_id)
        
        if track_info and track_info.get("id"):
            return {
                "valid": True,
                "track_info": {
                    "name": track_info.get("name"),
                    "artists": [a["name"] for a in track_info.get("artists", [])],
                    "uri": track_uri
                }
            }
        else:
            return {
                "valid": False,
                "error": "Track not found in Spotify"
            }
            
    except Exception as e:
        return {
            "valid": False,
            "error": f"Spotify API error: {str(e)}"
        }


def validate_and_add_tracks_to_queue(token_info: dict, track_uris: list) -> dict:
    """
    Validates a list of track URIs and adds only valid ones to the queue.
    
    Args:
        token_info: Spotify authentication token
        track_uris: List of Spotify track URIs
    
    Returns:
        dict with:
        - tracks_added: int
        - valid_tracks: list of valid URIs
        - invalid_tracks: list of invalid URIs with reasons
        - total_tracks: int
    """
    sp = spotipy.Spotify(auth=token_info["access_token"])
    
    valid_tracks = []
    invalid_tracks = []
    tracks_added = 0
    
    print(f"\n--- VALIDATING {len(track_uris)} TRACKS ---")
    
    for track_uri in track_uris:
        validation = validate_track_uri(token_info, track_uri)
        
        if validation["valid"]:
            valid_tracks.append(track_uri)
            track_info = validation["track_info"]
            track_name = track_info["name"]
            artists = ", ".join(track_info["artists"])
            print(f"✅ Valid: {track_name} - {artists}")
            
            # Try to add to queue
            try:
                sp.add_to_queue(track_uri)
                tracks_added += 1
            except Exception as e:
                print(f"⚠️  Error adding to queue: {e}")
                invalid_tracks.append({
                    "uri": track_uri,
                    "reason": f"Queue error: {str(e)}"
                })
        else:
            error_msg = validation.get("error", "Unknown error")
            invalid_tracks.append({
                "uri": track_uri,
                "reason": error_msg
            })
            print(f"❌ Invalid: {track_uri} - {error_msg}")
    
    print(f"\n--- VALIDATION COMPLETE ---")
    print(f"✅ Valid tracks: {len(valid_tracks)}")
    print(f"❌ Invalid tracks: {len(invalid_tracks)}")
    print(f"📝 Added to queue: {tracks_added}")
    
    return {
        "tracks_added": tracks_added,
        "valid_tracks": valid_tracks,
        "invalid_tracks": invalid_tracks,
        "total_tracks": len(track_uris)
    }

