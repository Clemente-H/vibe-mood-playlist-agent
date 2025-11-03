import spotipy

# This service file contains the core logic for interacting with the Spotify API.
# It is used by the routers to expose functionality via HTTP endpoints and by the agent flow.

def get_user_context(token_info: dict):
    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        top_tracks = sp.current_user_top_tracks(limit=20, time_range="medium_term")["items"]
        top_artists = sp.current_user_top_artists(limit=20, time_range="medium_term")["items"]
        recently_played = sp.current_user_recently_played(limit=20)["items"]

        return {
            "top_tracks": top_tracks,
            "top_artists": top_artists,
            "recently_played": recently_played
        }
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
