# agents/personalized_agent.py
"""
PersonalizedAgent: Searches for music in the user's personal library.
"""
from google.adk.agents import LlmAgent

from agents.prompts import PERSONALIZED_PROMPT


def _format_user_library(user_context: dict) -> str:
    """Formats user library with URIs for PersonalizedAgent."""
    lines = []
    
    # Top tracks with URIs
    top_tracks = user_context.get("top_tracks", [])
    if top_tracks:
        lines.append("YOUR TOP TRACKS (Most Played):")
        for i, track in enumerate(top_tracks[:20], 1):
            name = track.get("name", "Unknown")
            artists = ", ".join([
                a.get("name", "") for a in track.get("artists", [])
            ])
            uri = track.get("uri", "")
            lines.append(f"  {i}. {name} - {artists}")
            lines.append(f"     {uri}")
    
    # Recently played with URIs
    recently = user_context.get("recently_played", [])
    if recently:
        lines.append("\nRECENTLY PLAYED:")
        for i, track in enumerate(recently[:10], 1):
            name = track.get("name", "Unknown")
            artists = ", ".join([
                a.get("name", "") for a in track.get("artists", [])
            ])
            uri = track.get("uri", "")
            lines.append(f"  {i}. {name} - {artists}")
            lines.append(f"     {uri}")
    
    # Top artists for context
    top_artists = user_context.get("top_artists", [])
    if top_artists:
        lines.append("\nYOUR FAVORITE ARTISTS:")
        for artist in top_artists[:5]:
            name = artist.get("name", "Unknown")
            genres = ", ".join(artist.get("genres", [])[:3])
            lines.append(f"  • {name} ({genres})")
    
    return "\n".join(lines)


def create_personalized_agent(
    user_context: dict,
    user_message: str,
    output_key: str = None
) -> LlmAgent:
    """
    Factory function that creates a PersonalizedAgent with the user's
    complete musical context.
    
    Args:
        user_context: User context (top_tracks, playlists, etc.)
        user_message: User's request/message
        output_key: Key to store the result in session.state
    
    Returns:
        LlmAgent configured with user library
    """
    # Format user library with URIs
    user_library_str = _format_user_library(user_context)
    
    # Format prompt with user library and message
    formatted_prompt = PERSONALIZED_PROMPT.format(
        user_message=user_message,
        user_library=user_library_str
    )

    # Create agent WITHOUT tools (context is already in prompt)
    personalized_agent = LlmAgent(
        name="PersonalizedAgent",
        model="gemini-2.5-flash",
        instruction=formatted_prompt,
        description="Researches user's favorite music from their library.",
        tools=[],  # No tools needed, context is in prompt
        output_key=output_key
    )

    return personalized_agent
