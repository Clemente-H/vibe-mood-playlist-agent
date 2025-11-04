# agents/scout_agent.py
"""
ScoutAgent: Busca música nueva en la base de datos local (8M+ canciones).
"""
from google.adk.agents import LlmAgent
from agents.tools import search_local_db_by_mood
from agents.prompts import SCOUT_PROMPT


def create_scout_agent(user_message: str, output_key: str = None) -> LlmAgent:
    """Factory function que crea un nuevo ScoutAgent."""
    formatted_prompt = SCOUT_PROMPT.format(user_message=user_message)
    return LlmAgent(
        name="ScoutAgent",
        model="gemini-2.5-pro",
        instruction=formatted_prompt,
        description="Researches new music from the database.",
        tools=[search_local_db_by_mood],
        output_key=output_key
    )
