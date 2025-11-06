from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from dotenv import load_dotenv
import os
from starlette.middleware.sessions import SessionMiddleware

# Import the new router
from routers import spotify
from spotify_service import get_user_context, get_current_queue, get_spotify_oauth, get_access_token
from agents.agent_manager import run_agent_with_context

load_dotenv()

app = FastAPI()

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY"),
)

# Include the spotify router
app.include_router(spotify.router)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/login")
def login():
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

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/")

@app.post("/chat")
async def chat(request: Request, chat_request: ChatRequest):
    import spotipy
    from spotify_service import add_to_queue
    
    token_info = request.session.get("token_info")
    if not token_info:
        return {"error": "User not authenticated"}

    # Get user ID from Spotify
    sp = spotipy.Spotify(auth=token_info["access_token"])
    user_info = sp.current_user()
    user_id = user_info["id"]

    # --- Caching Logic for User Profile ---
    user_profile = request.session.get("user_profile")
    if not user_profile:
        print("--- No profile in session, fetching... ---")
        user_profile = get_user_context(token_info)
        request.session["user_profile"] = user_profile
    else:
        print("--- Found profile in session cache. ---")
    # -------------------------------------

    # Always get the real-time queue
    current_queue = get_current_queue(token_info)

    # Combine cached profile with real-time queue for full context
    spotify_context = {
        "user_profile": user_profile,
        "queue": current_queue
    }

    # Run the agent with the full context
    agent_result = await run_agent_with_context(
        user_message=chat_request.message,
        spotify_context=spotify_context,
        user_id=user_id
    )

    # Check if playlist was generated successfully
    if agent_result.get("status") == "success":
        playlist = agent_result.get("playlist", [])
        
        # Add all tracks to Spotify queue
        tracks_added = 0
        for track_uri in playlist:
            try:
                add_to_queue(token_info, track_uri)
                tracks_added += 1
            except Exception as e:
                print(f"Error adding {track_uri} to queue: {e}")
        
        return {
            "status": "success",
            "message": f"Added {tracks_added} songs to your queue!",
            "total_tracks": len(playlist),
            "playlist_preview": playlist[:5]  # Show first 5 URIs
        }
    else:
        return {
            "status": "error",
            "message": agent_result.get("message", "Failed to generate playlist")
        }