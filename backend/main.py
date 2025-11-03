from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from spotify.auth import get_spotify_oauth, get_authorize_url, get_access_token
from agents.main_agent import run_agent
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    colors: list[str]
    token_info: dict # For now, we pass the token in the request

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/login")
def login():
    oauth = get_spotify_oauth()
    auth_url = get_authorize_url(oauth)
    return RedirectResponse(auth_url)

@app.get("/callback")
def callback(request: Request):
    code = request.query_params.get("code")
    oauth = get_spotify_oauth()
    token_info = get_access_token(oauth, code)
    # For now, just return the token info
    # In a real app, you'd store this in a session
    return {"token_info": token_info}

@app.post("/chat")
def chat(chat_request: ChatRequest):
    track_uris = run_agent(
        message=chat_request.message,
        colors=chat_request.colors,
        token_info=chat_request.token_info,
    )
    return {"track_uris": track_uris}
