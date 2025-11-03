# Mood Vibe Curator - Backend

This backend is responsible for the agent-based music curation for the Mood Vibe Curator application.

---

## To Do

### 1. Environment Setup
- [ ] Create and activate a Python virtual environment.
- [ ] Install dependencies from `requirements.txt`: `pip install -r requirements.txt`.
- [ ] Create a `.env` file and add the following environment variables:
  ```
  SPOTIPY_CLIENT_ID=your_spotify_client_id
  SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
  SPOTIPY_REDIRECT_URI=http://localhost:8000/callback
  GOOGLE_APPLICATION_CREDENTIALS=path/to/your/google/credentials.json
  ```

### 2. Spotify Authentication
- [ ] Implement the OAuth 2.0 Authorization Code Flow.
- [ ] Create a `/login` endpoint in FastAPI to redirect to the Spotify authorization page.
- [ ] Create a `/callback` endpoint in FastAPI to handle the callback from Spotify, get the access token, and store it.

### 3. Agent Development (ADK)
- [ ] **MoodAnalysisAgent:**
  - [ ] Create an agent that takes a user's mood (text and colors) as input.
  - [ ] Use the Gemini API to analyze the mood and generate a detailed music recommendation prompt.
- [ ] **MusicCurationAgent:**
  - [ ] Create an agent that takes the music recommendation prompt as input.
  - [ ] Use the `spotipy` library to search for tracks on Spotify.
  - [ ] Use the `spotipy` library to add the found tracks to the user's queue.
- [ ] **Main Agent (Orchestrator):**
  - [ ] Create a main agent that orchestrates the `MoodAnalysisAgent` and `MusicCurationAgent`.

### 4. API Endpoints (FastAPI)
- [ ] Create a `/chat` endpoint that receives the user's message, triggers the main agent, and returns the curated tracks.
- [ ] Create a `/player` endpoint to get the current playback state from Spotify and update the frontend's `MusicPlayer` component.

---
