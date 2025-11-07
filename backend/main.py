from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import json

from dotenv import load_dotenv
import os
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware

# Import the new router
from routers import spotify
from spotify_service import get_user_context, get_current_queue, get_spotify_oauth, get_access_token
from agents.agent_manager import run_agent_with_context

load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY"),
    same_site="lax",
    https_only=False
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
    return RedirectResponse("http://127.0.0.1:3000/")

@app.get("/token")
def me(request: Request):
    token_info = request.session.get("token_info")
    if not token_info:
        raise HTTPException(status_code=401, detail="Not logged in")
    
    return {'access_token': token_info.get("access_token")}

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/")

@app.post("/chat")
async def chat(request: Request, chat_request: ChatRequest):
    token_info = request.session.get("token_info")
    if not token_info:
        return {"error": "User not authenticated"}

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
    full_context = {
        "user_profile": user_profile,
        "queue": current_queue
    }

    # Run the agent with the full context
    agent_plan = await run_agent_with_context(chat_request.message, full_context)

    # For now, just print and return the plan
    print("--- AGENT PLAN RECEIVED ---")
    print(agent_plan)
    print("---------------------------")

    # TODO: Implement the plan execution logic here

    return {"status": "Plan received", "plan": agent_plan}
