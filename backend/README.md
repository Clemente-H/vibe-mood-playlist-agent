# Mood Vibe Curator - Backend

This backend is responsible for the agent-based music curation for the Mood Vibe Curator application.

---

## Architecture

The backend is designed with a clean, modular architecture to separate concerns:

- **`main.py`**: The main application entry point. It initializes the FastAPI app, adds middleware (like sessions), and includes the routers. It only contains the core endpoints like `/login`, `/callback`, and `/chat`.

- **`routers/`**: This directory holds the API endpoints exposed to the client. For example, `routers/spotify.py` contains all endpoints for direct playback control (`/spotify/play`, `/spotify/pause`, etc.).

- **`services/`**: This layer contains the core business logic. We have two main services:
    - **`spotify_service.py`**: Handles all communication with the Spotify API (fetching user context, adding songs to queue, etc.). It also preprocesses the raw data from Spotify into a clean format.
    - **`database_service.py`**: Will handle all communication with the local DuckDB song database (searching for songs by mood, genre, etc.).

- **`agent_manager.py`**: The brain of the agent operation. It receives context from the `/chat` endpoint, formats the prompt (from `prompts.py`), calls the agent (LLM), and returns the agent's plan.

- **`prompts.py`**: A dedicated file to store and manage the large text prompts sent to the agent.

---

## Project Status

### ✅ Completed

- **Authentication**: Full Spotify OAuth 2.0 flow with secure session management for tokens.
- **Modular Architecture**: Refactored the application into a clean structure with `routers` and `services`.
- **Playback Control API**: A full suite of endpoints for direct control over Spotify playback and playlist management:
    - `/spotify/play`, `/spotify/pause`, `/spotify/stop`, `/spotify/skip`, `/spotify/previous`
    - `/spotify/search`, `/spotify/queue_add`, `/spotify/current_playback`
    - `/spotify/create_playlist_from_queue`, `/spotify/add_to_likes`, `/spotify/user_playlists`
- **Rich User Context**: Created a `get_user_context` function that fetches and **preprocesses** a user's top tracks, top artists, and recently played songs into a clean, agent-ready format.
- **Initial Agent Structure**: Set up `agent_manager.py` and `prompts.py` in preparation for agent integration.

### 🚀 Next Steps: Agent & Database Implementation

1.  **Database Setup**:
    - [ ] Add `duckdb` to `requirements.txt`.
    - [ ] Create `database_service.py`.
    - [ ] Implement a connection to the DuckDB file.
    - [ ] Implement a `find_songs_by_mood` function that queries the local database based on audio features (e.g., `valence`, `energy`).

2.  **Agent Integration**:
    - [ ] Update `agent_manager.py` to correctly format the preprocessed `user_profile` and `queue` context into the prompt string.
    - [ ] Update `prompts.py` to include the new `search_local_database` tool for the agent to use.

3.  **Plan Execution**:
    - [ ] In the `/chat` endpoint, implement the logic to parse the JSON plan returned by the agent.
    - [ ] Execute the plan by calling the appropriate functions from `spotify_service.py` and `database_service.py`.

4.  **Advanced (Future)**:
    - [ ] Implement specialist agents (`MoodAgent`, `ScoutAgent`) within the `agent_manager`.
    - [ ] Implement a feedback loop for the agent to learn from user actions (e.g., skipping a song).
