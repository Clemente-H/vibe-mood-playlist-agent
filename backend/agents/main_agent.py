from agents.mood_analysis_agent import analyze_mood
from agents.music_curation_agent import curate_music

def run_agent(message: str, colors: list[str], token_info: dict) -> list[str]:
    """
    Runs the main agent to curate music based on the user's mood.

    Args:
        message: The user's message describing their mood.
        colors: A list of hex color codes representing the mood.
        token_info: The user's Spotify token information.

    Returns:
        A list of Spotify track URIs.
    """

    # 1. Analyze the mood
    music_prompt = analyze_mood(message, colors)

    # 2. Curate music
    track_uris = curate_music(token_info, music_prompt)

    return track_uris
