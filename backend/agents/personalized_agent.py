# agents/personalized_agent.py
"""
PersonalizedAgent: Searches for music in the user's personal library.
"""
from google.adk.agents import LlmAgent

from agents.prompts import PERSONALIZED_PROMPT
from agents.context_formatter import format_for_personalized_agent


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
    # Format user library using centralized formatter
    user_library_str = format_for_personalized_agent(user_context)
    
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
        description="Searches user's music collection from their library.",
        tools=[],  # No tools, context in prompt
        output_key=output_key
    )

    return personalized_agent
