from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import json

from dotenv import load_dotenv
import os
from starlette.middleware.cors import CORSMiddleware
import os

# Import the new router
from routers import spotify
from spotify_service import get_user_context, get_current_queue, get_spotify_oauth, get_access_token
from agents.agent_manager import run_agent_with_context

load_dotenv()

app = FastAPI()

# Get frontend URL from environment variable, with a default for local dev
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:3000")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL], # Use the variable here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session middleware removed - using token-based auth only to avoid shared sessions
# is_production = FRONTEND_URL.startswith("https://")



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
    if not code:
        # User denied access
        return RedirectResponse(f"{FRONTEND_URL}/")

    token_info = get_access_token(code)
    # Don't store in session - pass to frontend via URL
    # Frontend will store in localStorage (per-user)
    access_token = token_info.get("access_token", "")
    return RedirectResponse(f"{FRONTEND_URL}/?token={access_token}")

def get_token_info(request: Request) -> dict:
    """Get token info from Authorization header only"""
    # Only use Authorization header (no sessions)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        access_token = auth_header.replace("Bearer ", "")
        return {"access_token": access_token}

    return None

@app.get("/token")
def me(request: Request):
    token_info = get_token_info(request)
    if not token_info:
        raise HTTPException(status_code=401, detail="Not logged in")

    return {'access_token': token_info.get("access_token")}

@app.get("/logout")
def logout(request: Request):
    # No session to clear - client handles logout
    return {"message": "Logout successful"}

@app.post("/chat")
async def chat(request: Request, chat_request: ChatRequest):
    import spotipy
    from spotify_service import validate_and_add_tracks_to_queue

    token_info = get_token_info(request)
    if not token_info:
        raise HTTPException(status_code=401, detail="User not authenticated")

    # Get user ID from Spotify
    sp = spotipy.Spotify(auth=token_info["access_token"])
    user_info = sp.current_user()
    user_id = user_info["id"]

    # Get user profile and queue (no caching without sessions)
    print("--- Fetching user profile... ---")
    user_profile = get_user_context(token_info)
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
        
        # Validate and add tracks to queue (done in spotify_service)
        validation_result = validate_and_add_tracks_to_queue(
            token_info,
            playlist
        )
        
        # Prepare response
        response = {
            "status": "success",
            "message": f"Added {validation_result['tracks_added']} songs to your queue!",
            "total_tracks": validation_result["total_tracks"],
            "valid_tracks": len(validation_result["valid_tracks"]),
            "invalid_tracks": len(validation_result["invalid_tracks"]),
            "playlist_preview": validation_result["valid_tracks"][:5]
        }
        
        if validation_result["invalid_tracks"]:
            response["warning"] = f"{len(validation_result['invalid_tracks'])} tracks were invalid and skipped"
            response["invalid_uris"] = validation_result["invalid_tracks"][:5]
            
        return response
    else:
        return {
            "status": "error",
            "message": agent_result.get("message", "Failed to generate playlist")
        }