# Vibe FM - System Architecture Flowchart

```mermaid
flowchart TB
    Start([User Describes Mood]) --> Frontend[Frontend - Next.js]
    
    Frontend -->|POST /chat| Backend[Backend API - FastAPI]
    
    Backend --> Auth{Authenticated?}
    Auth -->|No| Spotify[Spotify OAuth 2.0]
    Spotify --> Auth
    Auth -->|Yes| Context[Get User Context]
    
    Context --> UserData[Spotify Service]
    UserData -->|Fetch| SpotifyAPI[(Spotify API)]
    
    SpotifyAPI --> TopTracks[Top Tracks]
    SpotifyAPI --> TopArtists[Top Artists]
    SpotifyAPI --> Playlists[User Playlists]
    
    TopTracks --> Orchestrator[OrchestratorAgent<br/>Gemini-powered]
    TopArtists --> Orchestrator
    Playlists --> Orchestrator
    
    Orchestrator -->|Parallel Processing| Scout[ScoutAgent<br/>Discovery Engine]
    Orchestrator -->|Parallel Processing| Personal[PersonalizedAgent<br/>Familiar Favorites]
    
    Scout -->|search_all_songs| MainDB[(DuckDB<br/>8M+ Songs)]
    Personal -->|search_liked_songs| UserDB[(User-Specific<br/>Liked Songs)]
    
    MainDB -->|New Music| Scout
    UserDB -->|Familiar Music| Personal
    
    Scout --> NewSongs[New Recommendations]
    Personal --> FamiliarSongs[Personalized Picks]
    
    NewSongs --> Merger[MergerAgent<br/>Balance & Validate]
    FamiliarSongs --> Merger
    
    Merger --> Plan[JSON Plan<br/>Song URIs]
    
    Plan --> Execute[Execute Plan]
    Execute --> SpotifyService[Spotify Service]
    SpotifyService -->|Create/Update| Playlist[Spotify Playlist/Queue]
    
    Playlist --> Response[Response to Frontend]
    Response --> End([User Enjoys Music])
    
    style Start fill:#4285F4,color:#fff
    style End fill:#34A853,color:#fff
    style Orchestrator fill:#FBBC04,color:#000
    style Scout fill:#EA4335,color:#fff
    style Personal fill:#EA4335,color:#fff
    style Merger fill:#FBBC04,color:#000
    style MainDB fill:#666,color:#fff
    style UserDB fill:#666,color:#fff
```

## Key Components

### Frontend Layer
- **Next.js Interface**: Visual mood input with color palettes and text descriptions
- **Real-time Updates**: WebSocket-ready for live agent status

### Backend Layer (Cloud Run)
- **FastAPI Service**: RESTful API with async support
- **Spotify OAuth**: Secure authentication flow
- **Session Management**: User state persistence

### AI Agent System (ADK + Gemini)
1. **OrchestratorAgent**: Main coordinator using Gemini for mood analysis
2. **ScoutAgent**: Discovery engine searching 8M+ songs via DuckDB
3. **PersonalizedAgent**: Curates from user's listening history
4. **MergerAgent**: Balances new discoveries with familiar favorites

### Data Layer
- **DuckDB**: High-performance analytics database
  - Main tracks table: 8M+ songs with audio features
  - User-specific tables: Liked songs with preferences
- **Spotify API**: Real-time data and playback control

### Deployment
- **Google Cloud Run**: Serverless, auto-scaling containers
- **Stateless Design**: Each request is independent
- **Fast Cold Starts**: Optimized for serverless

## Data Flow Summary

1. User inputs mood → Frontend
2. Backend authenticates and fetches Spotify context
3. OrchestratorAgent analyzes mood with Gemini
4. Parallel agent execution:
   - ScoutAgent searches 8M+ song database
   - PersonalizedAgent queries user's liked songs
5. MergerAgent combines and balances results
6. Playlist created in Spotify
7. User receives perfectly curated music
