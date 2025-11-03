# Mood Vibe Curator - Backend

This backend is responsible for the agent-based music curation for the Mood Vibe Curator application.

---

## Architecture Flow

The application follows a specific architectural flow where FastAPI acts as the central orchestrator and the Agent acts as a recommendation engine.

1.  **Frontend -> FastAPI**: The user sends a natural language request (a "mood") to the `/chat` endpoint.
2.  **FastAPI -> Agent**: FastAPI passes the user's text to the Agent for processing.
3.  **Agent's Process**:
    *   The Agent analyzes the request. If it needs more context (e.g., for personalized recommendations), it uses a tool like `get_user_info`.
    *   This tool call is a request back to FastAPI. FastAPI then fetches the required data from Spotify (e.g., user's top artists) and passes it back to the Agent.
    *   With full context, the Agent queries its local song database (SQLite) and assembles a list of recommended song IDs and scores.
4.  **Agent -> FastAPI**: The Agent returns a final JSON object to FastAPI. This JSON is a direct command, like `{"function_to_call": "play_next", "arguments": {"songs": [...], "scores": {...}}}`.
5.  **FastAPI -> Spotify**: FastAPI parses the JSON and executes the command, calling the Spotify API to add the recommended songs to the user's queue.
6.  **FastAPI -> Frontend**: FastAPI confirms the action to the user.

---

## To Do

### Track 1: Core Functionality (MVP)

#### 1. Environment & Authentication
- [ ] **Environment Setup:**
    - [ ] Create and activate a Python virtual environment.
    - [ ] Install dependencies from `requirements.txt`.
    - [ ] Set up the `.env` file with Spotify and Google Cloud credentials.
- [ ] **Spotify Authentication:**
    - [ ] Implement the OAuth 2.0 flow with `/login` and `/callback` endpoints in FastAPI.
    - [ ] Store the user's access token securely (e.g., in a session).

#### 2. Agent & FastAPI Core
- [ ] **Agent Setup:**
    - [ ] Initialize a basic agent structure.
    - [ ] Implement agent's ability to access a local SQLite database of songs.
- [ ] **Agent Tools (`tools.py`):**
    - [ ] Create a `get_user_info` tool definition. This tool will not contain logic, but will signal to FastAPI that user context is needed.
- [ ] **FastAPI `/chat` Endpoint:**
    - [ ] Create the `/chat` endpoint that receives the user's text.
    - [ ] Implement the logic to call the Agent.
    - [ ] Add the capability to handle a `get_user_info` tool call from the agent by fetching data from Spotify and passing it back to the agent.
- [ ] **Plan Execution:**
    - [ ] Implement the logic for FastAPI to receive the final JSON plan from the Agent (e.g., `{"function_to_call": "play_next", ...}`).
    - [ ] Create the corresponding `play_next` function in FastAPI that calls the Spotify API to add songs to the queue.

### Track 2: Multi-Agent System & Intelligence

- [ ] **Sub-Agents (Personas):**
    - [ ] **Conservative Agent:** Recommends songs based on the user's top artists.
    - [ ] **Explorer Agent:** Recommends less-known artists that match the mood.
    - [ ] **Popular Songs Agent:** Recommends popular songs that match the mood.
- [ ] **Orchestrator Agent:**
    - [ ] Implement a top-level agent that receives the user's mood and context.
    - [ ] This agent will decide which sub-agents to call and how to weigh their recommendations to generate the final song list.
- [ ] **Feedback Loop:**
    - [ ] Implement a mechanism for the agent to receive feedback (e.g., when a user skips or removes a song).
    - [ ] Use this feedback to refine future recommendations.


* Importante:
al final el agente lo unico que es es una funcione entre chat y play next.
