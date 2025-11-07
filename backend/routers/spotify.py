from fastapi import APIRouter, Request, HTTPException
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

class PlayFromQueueBody(BaseModel):
    index: int

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

@router.get("/queue")
async def get_queue(request: Request):
    token_info = request.session.get("token_info")
    if not token_info:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return spotify_service.get_current_queue(token_info)

@router.post("/play_from_queue")
async def play_from_queue(request: Request, body: PlayFromQueueBody):
    """
    Reconstruye la reproducción a partir del item 'index' de la cola actual.
    No hay API para “saltar” directo a un item de la cola; esto la reemplaza con las URIs desde ese punto.
    """
    token_info = request.session.get("token_info")
    if not token_info:
        raise HTTPException(status_code=401, detail="User not authenticated")

    queue_data = spotify_service.get_current_queue(token_info)
    if isinstance(queue_data, dict) and queue_data.get("error"):
        raise HTTPException(status_code=400, detail=queue_data["error"])

    if "queue" not in queue_data:
        raise HTTPException(status_code=400, detail="No queue available")

    queue_items = queue_data["queue"] or []
    if body.index < 0 or body.index >= len(queue_items):
        raise HTTPException(status_code=400, detail="Index out of range")

    uris = [item.get("uri") for item in queue_items[body.index:] if item.get("uri")]
    if not uris:
        raise HTTPException(status_code=400, detail="No URIs available from selected index")

    result = spotify_service.start_playback_with_uris(token_info, uris)
    if isinstance(result, dict) and result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])

    return {"message": f"Playing from queue index {body.index}", "count": len(uris)}
