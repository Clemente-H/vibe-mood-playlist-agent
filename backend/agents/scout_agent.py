# agents/scout_agent.py
"""
ScoutAgent: Searches for new music in the local database (8M+ songs).
Includes the search_local_db_by_mood tool used exclusively by this agent.
"""
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool as Tool

from agents.prompts import SCOUT_PROMPT
from data_spotify.database_service import search_all_songs


@Tool
def search_local_db_by_mood(
    energy_min: float,
    energy_max: float,
    valence_min: float,
    valence_max: float,
    danceability_min: float,
    danceability_max: float,
    acousticness_min: float,
    acousticness_max: float,
    tempo_min: float,
    tempo_max: float,
    limit: int
) -> dict:
    """
    Searches the local song database using audio feature ranges.
    ALL parameters are REQUIRED - you must specify ranges for all audio features.

    Args:
        energy_min: Minimum energy (0-1). High = loud, fast, noisy. REQUIRED.
        energy_max: Maximum energy (0-1). REQUIRED.
        valence_min: Minimum valence (0-1). High = happy, cheerful. REQUIRED.
        valence_max: Maximum valence (0-1). REQUIRED.
        danceability_min: Minimum danceability (0-1). How suitable for dancing. REQUIRED.
        danceability_max: Maximum danceability (0-1). REQUIRED.
        acousticness_min: Minimum acousticness (0-1). Acoustic vs electronic. REQUIRED.
        acousticness_max: Maximum acousticness (0-1). REQUIRED.
        tempo_min: Minimum tempo in BPM. REQUIRED.
        tempo_max: Maximum tempo in BPM. REQUIRED.
        limit: Number of songs to return. REQUIRED.

    Returns:
        dict with list of found songs
    """
    # Build mood_params dict - all parameters are now required
    mood_params = {
        'energy': {'min': energy_min, 'max': energy_max},
        'valence': {'min': valence_min, 'max': valence_max},
        'danceability': {'min': danceability_min, 'max': danceability_max},
        'acousticness': {'min': acousticness_min, 'max': acousticness_max},
        'tempo': {'min': tempo_min, 'max': tempo_max}
    }
    
    results = search_all_songs(mood_params, None, limit)
    return {"results": results}


def create_scout_agent(user_message: str, output_key: str = None) -> LlmAgent:
    """
    Factory function that creates a new ScoutAgent.
    
    Args:
        user_message: User's request/message
        output_key: Key to store the result in session.state
    
    Returns:
        LlmAgent configured for database search
    """
    formatted_prompt = SCOUT_PROMPT.format(user_message=user_message)
    return LlmAgent(
        name="ScoutAgent",
        model="gemini-2.5-flash",
        instruction=formatted_prompt,
        description="Researches new music from the database.",
        tools=[search_local_db_by_mood],
        output_key=output_key
    )
