# Mood Vibe Curator - Backend

This backend is responsible for the agent-based music curation for the Mood Vibe Curator application.

---

## Architecture

The backend uses a modular, service-oriented architecture:

- **`main.py`**: The application entry point. Handles app initialization, middleware, and core endpoints (`/login`, `/chat`, etc.).

- **`routers/`**: Defines the HTTP API layer. `spotify.py` exposes direct Spotify controls to the frontend.

- **`spotify_service.py`**: The service layer for all communication with the Spotify API. It handles data fetching, preprocessing, and playback commands.

- **`data_spotify/database_service.py`**: The service layer for all communication with the local **DuckDB** database. It will manage the main `tracks` table and user-specific tables.

- **`agents/`**: Contains the agent definitions. The `orchestrator.py` will house the main agent, while other files will define specialist agents.

- **`agent_manager.py`**: The 'brain' that orchestrates the agent flow. It gets context from `/chat`, prepares prompts, calls the agent(s), and will eventually execute the returned plan.

- **`prompts.py`**: Stores all text prompts for the agents.

---

## Agent & Data Flow

Our system uses a powerful, multi-agent approach for recommendations:

1.  **User-Specific Table Creation**: On first use, a process fetches all of a user's "Liked Songs" from Spotify, along with their audio features. This data is then used to create a dedicated table (e.g., `liked_songs_user123`) inside our main DuckDB database file. This provides a persistent, queryable database of the user's personal taste.

2.  **Agent Specialists**: We use two main specialist agents:
    - **`PersonalizedAgent`**: This agent's tool (`search_liked_songs`) queries the user-specific `liked_songs_...` table. It finds songs the user **already loves** that match the current mood.
    - **`ScoutAgent`**: This agent's tool (`search_all_songs`) queries the main `tracks` table (8M+ songs). It finds **new songs** that match the user's taste and mood, acting as a discovery engine.

3.  **Orchestration**: A main `OrchestratorAgent` receives the user's request, calls one or both specialist agents, and combines their results into a final, validated list of song URIs.

4.  **Plan Generation & Execution**: The final list is formatted into a JSON plan (e.g., `{"function_to_call": "add_songs_to_queue", ...}`). The `/chat` endpoint receives this plan and calls the appropriate functions in `spotify_service.py` to execute it.

---

## Project Status

### ✅ Completed

- **Authentication**: Full Spotify OAuth 2.0 flow with secure session management.
- **Modular Architecture**: Refactored into `routers`, `services`, and `agents` directories.
- **Full Playback API**: A comprehensive suite of endpoints for direct Spotify control.
- **Rich User Context**: A `get_user_context` function that fetches and preprocesses user data.
- **Initial Agent Structure**: Scaffolding for `agent_manager`, `prompts`, and `agents` is in place.

### 🚀 Next Steps: Agent & Database Implementation

1.  **Database Setup (`database_service.py`)**:
    - [ ] Add `duckdb` to `requirements.txt`.
    - [ ] Create `data_spotify/database_service.py`.
    - [ ] Implement a function to connect to the DuckDB file.
    - [ ] Implement `create_or_update_user_table` to sync a user's liked songs into a dedicated table.
    - [ ] Implement `search_liked_songs` and `search_all_songs` to query the respective tables based on audio features.

2.  **Agent Integration (`agent_manager.py`)**:
    - [ ] Implement the logic to format the `user_profile` and `queue` context into the prompt string.
    - [ ] Update `prompts.py` to include the new database search tools.

3.  **Plan Execution (`main.py`)**:
    - [ ] In the `/chat` endpoint, implement the logic to parse the agent's JSON plan.
    - [ ] Execute the plan by calling functions from `spotify_service.py` and `database_service.py`.

