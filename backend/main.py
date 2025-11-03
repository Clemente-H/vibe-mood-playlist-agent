from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from spotify.auth import get_spotify_oauth, get_authorize_url, get_access_token
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

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
