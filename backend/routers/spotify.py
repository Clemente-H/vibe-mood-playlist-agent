from fastapi import APIRouter, Request
from pydantic import BaseModel
import spotify_service

# This router handles all the direct Spotify control endpoints.
# It uses the functions from spotify_service.py to interact with the Spotify API.

router = APIRouter(
    prefix="/spotify",
    tags=["Spotify"],
)

class PlayRequest(BaseModel):
    song_uri: str

class SearchRequest(BaseModel):
    query: str

class PlaylistRequest(BaseModel):
    playlist_name: str

class TrackUriRequest(BaseModel):
    track_uri: str

@router.post("/play")
async def play_song(request: Request, play_request: PlayRequest):
    token_info = request.session.get("token_info")
    if not token_info:
        return {"error": "User not authenticated"}
    spotify_service.add_to_queue(token_info, play_request.song_uri)
    return spotify_service.start_playback(token_info)

@router.post("/pause")
async def pause_playback(request: Request):
    token_info = request.session.get("token_info")
    if not token_info:
        return {"error": "User not authenticated"}
    return spotify_service.pause_playback(token_info)

@router.post("/stop")
async def stop_playback(request: Request):
    token_info = request.session.get("token_info")
    if not token_info:
        return {"error": "User not authenticated"}
    return spotify_service.stop_playback(token_info)

@router.post("/skip")
async def skip_track(request: Request):
    token_info = request.session.get("token_info")
    if not token_info:
        return {"error": "User not authenticated"}
    return spotify_service.next_track(token_info)

@router.post("/previous")
async def previous_track(request: Request):
    token_info = request.session.get("token_info")
    if not token_info:
        return {"error": "User not authenticated"}
    return spotify_service.previous_track(token_info)

@router.post("/queue_add")
async def add_to_queue(request: Request, play_request: PlayRequest):
    token_info = request.session.get("token_info")
    if not token_info:
        return {"error": "User not authenticated"}
    return spotify_service.add_to_queue(token_info, play_request.song_uri)

@router.post("/create_playlist_from_queue")
async def create_playlist_from_queue(request: Request, playlist_request: PlaylistRequest):
    token_info = request.session.get("token_info")
    if not token_info:
        return {"error": "User not authenticated"}
    return spotify_service.create_playlist_from_queue(token_info, playlist_request.playlist_name)

@router.post("/add_to_likes")
async def add_to_likes(request: Request, track_uri_request: TrackUriRequest):
    token_info = request.session.get("token_info")
    if not token_info:
        return {"error": "User not authenticated"}
    return spotify_service.add_track_to_likes(token_info, track_uri_request.track_uri)

@router.get("/user_playlists")
async def get_user_playlists(request: Request):
    token_info = request.session.get("token_info")
    if not token_info:
        return {"error": "User not authenticated"}
    return spotify_service.get_user_playlists(token_info)

@router.get("/current_playback")
async def get_current_playback(request: Request):
    token_info = request.session.get("token_info")
    if not token_info:
        return {"error": "User not authenticated"}
    return spotify_service.get_current_playback(token_info)

@router.post("/search")
async def search_track(request: Request, search_request: SearchRequest):
    token_info = request.session.get("token_info")
    if not token_info:
        return {"error": "User not authenticated"}
    return spotify_service.search_track(token_info, search_request.query)

@router.post("/user_context")
def get_user_context(request: Request):
    token_info = request.session.get("token_info")
    if not token_info:
        return {"error": "User not authenticated"}
    return spotify_service.get_user_context(token_info)
