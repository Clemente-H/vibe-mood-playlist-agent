# Vibe.FM

> An intelligent music agent that understands your emotions better than Spotify's DJ.

[![Cloud Run Hackathon 2025](https://img.shields.io/badge/Cloud%20Run-Hackathon%202025-4285F4)](https://run.devpost.com)

---

## About The Project

There are moments we can't explain and feelings we can't quite put into words. But music always seems to understand.

**Vibe.FM** is a bridge to that understanding. It's an intelligent music agent that translates your unique emotional state into the perfect playlist. Through a beautiful, interactive interface, you can describe your vibe with words and colors. Our multi-agent system then analyzes your request, blending fresh music discovery with the comfort of your personal favorites, and automatically curates a unique queue for you, right in your Spotify.

## Core Features

- **Interactive UI**: A dynamic, animated interface with a color-shifting background that reacts to your inputs.
- **Mood-Based Playlist Generation**: Simply tell the chat how you're feeling (e.g., "a rainy afternoon" or "an energetic workout"), and the agent system will build a queue for you.
- **Intelligent Agent System**:
    - A `ScoutAgent` discovers new music matching your vibe.
    - A `PersonalizedAgent` selects tracks from your own library that you already love.
    - A `MergerAgent` intelligently blends both lists for the perfect mix of discovery and comfort.
- **Full Spotify Integration**:
    - Secure OAuth2 login with Spotify.
    - Automatically adds generated playlists to your Spotify queue.
    - A full suite of playback controls (play, pause, skip, etc.) directly from the app.
- **Performance Optimized**: User profiles are cached on the server-side to ensure fast interactions after the first request.

## Getting Started

### Prerequisites

- Python 3.10+ & Poetry (for backend)
- Node.js & npm (for frontend)
- A Spotify Developer App for API keys.

### Backend Setup

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Create a `.env` file from the `.env.example` and fill in your Spotify API credentials.
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run the server:
    ```bash
    uvicorn main:app --reload --port 8000
    ```
    The backend will be running at `http://127.0.0.1:8000`.

### Frontend Setup

1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```
    The frontend will be available at `http://127.0.0.1:3000`.

## System Architecture

The application follows a decoupled frontend/backend architecture. The core logic resides in the backend's multi-agent system, which processes user requests to generate playlists.

- **Frontend**: A Next.js single-page application responsible for all UI and user interaction.
- **Backend**: A FastAPI server that handles:
    1.  **Authentication**: A secure, session-based OAuth2 flow with Spotify.
    2.  **Agent Logic**: The `/chat` endpoint orchestrates the agent system to generate playlists.
    3.  **Spotify Control**: A full API (`/spotify/*`) to control the Spotify player.

For a more detailed breakdown of the agent flow, see the [ARCHITECTURE.md](ARCHITECTURE.md) file.

## API Endpoints

The backend exposes the following main endpoints:

-   `/login`: Initiates Spotify authentication.
-   `/callback`: Handles the OAuth2 callback from Spotify.
-   `/token`: Checks if the user is authenticated.
-   `/chat`: The main endpoint for generating playlists based on a user's message.
-   `/spotify/*`: A collection of endpoints for player control (e.g., `/spotify/play`, `/spotify/pause`, `/spotify/skip`).

## Technology Stack

-   **Backend**:
    -   Python
    -   FastAPI
    -   Spotipy (Spotify API Client)
    -   Google ADK (for Agent implementation)
-   **Frontend**:
    -   Next.js
    -   React
    -   Framer Motion (for animations)
    -   Tailwind CSS
    -   Axios
-   **Deployment**:
    -   Docker
    -   Google Cloud Run (planned)

---

## Team

- Gonzalo
- Gruñon (Cesar)
- Clemente
