# Vibe Mood Playlist Agent - Tutorial

AI-powered music playlist generator using Google Gemini agents and Spotify API.

## Quick Start

1. **Start server**: `cd backend; uvicorn main:app --reload`
2. **Open docs**: `http://127.0.0.1:8000/docs`
3. **Login**: Go to `http://127.0.0.1:8000/login` in another tab
4. **Test Spotify**: Try endpoints in `/docs` (optional)
5. **Make request**: Use `POST /chat` with your message

---

## How It Works

### Agent Architecture

The system uses 3 AI agents working in parallel and sequence:

**ScoutAgent** - Searches 8M+ songs database
- Uses audio features (energy, valence, danceability, tempo, etc.)
- Finds 20 new songs matching the mood
- Returns diverse tracks you might not know

**PersonalizedAgent** - Selects from your library
- Analyzes your top tracks and artists
- Picks 20 songs from your favorites
- Matches them to the requested vibe

**MergerAgent** - Combines results
- Mixes 70-80% personalized + 20-30% new discoveries
- Detects quantity from request ("all night" = 60-80 songs, "1 hour" = 20)
- Removes duplicates and creates final playlist

### Flow

```
User message → ScoutAgent + PersonalizedAgent (parallel) → MergerAgent → Spotify Queue
```

---
