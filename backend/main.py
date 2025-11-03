from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from music_agent.tools.spotify_tools import get_access_token
from music_agent.agent import root_agent
from dotenv import load_dotenv
import spotipy
import os
from starlette.middleware.sessions import SessionMiddleware

load_dotenv()

app = FastAPI()

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY"),
)

class ChatRequest(BaseModel):
    message: str

class PlayRequest(BaseModel):
    song_uri: str

class SearchRequest(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/login")
def login():
    # The login logic remains the same, but we need to get the auth_url from the tool
    from music_agent.tools.spotify_tools import get_spotify_oauth
    oauth = get_spotify_oauth()
    auth_url = oauth.get_authorize_url()
    return RedirectResponse(auth_url)

@app.get("/callback")
def callback(request: Request):
    code = request.query_params.get("code")
    token_info = get_access_token(code)
    request.session["token_info"] = token_info
    # Redirect to the frontend, which will now have the session cookie
    return RedirectResponse("http://localhost:3000/")

@app.post("/chat")
async def chat(request: Request, chat_request: ChatRequest):
    token_info = request.session.get("token_info")
    if not token_info:
        return {"error": "User not authenticated"}

    response = await root_agent.run_async(
        chat_request.message,
        tool_context={"token_info": token_info}
    )
    print("Agent response:", response)
    return {"response": response}

@app.post("/tools/get_user_info")
def get_user_info(request: Request):
    token_info = request.session.get("token_info")
    if not token_info:
        return {"error": "User not authenticated"}

    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        top_tracks = sp.current_user_top_tracks(limit=10, time_range="short_term")
        return {"top_tracks": top_tracks["items"]}
    except Exception as e:
        return {"error": f"Error fetching user info: {e}"}

@app.post("/play")
async def play_song(request: Request, play_request: PlayRequest):
    token_info = request.session.get("token_info")
    if not token_info:
        return {"error": "User not authenticated"}

    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        sp.add_to_queue(play_request.song_uri)
        sp.start_playback()
        return {"message": f"Added {play_request.song_uri} to queue and started playback."}
    except Exception as e:
        return {"error": f"Error playing song: {e}"}

@app.post("/pause")
async def pause_playback(request: Request):
    token_info = request.session.get("token_info")
    if not token_info:
        return {"error": "User not authenticated"}

    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        sp.pause_playback()
        return {"message": "Playback paused."}
    except Exception as e:
        return {"error": f"Error pausing playback: {e}"}

@app.post("/skip")
async def skip_track(request: Request):
    token_info = request.session.get("token_info")
    if not token_info:
        return {"error": "User not authenticated"}

    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        sp.next_track()
        return {"message": "Skipped to next track."}
    except Exception as e:
        return {"error": f"Error skipping track: {e}"}

@app.post("/queue_add")
async def add_to_queue(request: Request, play_request: PlayRequest):
    token_info = request.session.get("token_info")
    if not token_info:
        return {"error": "User not authenticated"}

    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        sp.add_to_queue(play_request.song_uri)
        return {"message": f"Added {play_request.song_uri} to queue."}
    except Exception as e:
        return {"error": f"Error adding to queue: {e}"}

@app.get("/current_playback")
async def get_current_playback(request: Request):
    token_info = request.session.get("token_info")
    if not token_info:
        return {"error": "User not authenticated"}

    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        current_playback = sp.current_playback()
        if current_playback:
            return {"current_playback": current_playback}
        else:
            return {"message": "No track currently playing."}
    except Exception as e:
        return {"error": f"Error fetching current playback: {e}"}

@app.post("/search")
async def search_track(request: Request, search_request: SearchRequest):
    token_info = request.session.get("token_info")
    if not token_info:
        return {"error": "User not authenticated"}

    sp = spotipy.Spotify(auth=token_info["access_token"])
    try:
        results = sp.search(q=search_request.query, type="track", limit=10)
        return {"results": results["tracks"]["items"]}
    except Exception as e:
        return {"error": f"Error searching track: {e}"}
