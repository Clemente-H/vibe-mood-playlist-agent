# agents/personalized_agent.py
"""
PersonalizedAgent: Busca música en la biblioteca personal del usuario.
"""
from google.adk.agents import LlmAgent
from agents.tools import create_get_user_context_tool
from agents.prompts import PERSONALIZED_PROMPT


def create_personalized_agent(
    token_info: dict,
    user_message: str,
    output_key: str = None
) -> LlmAgent:
    """
    Factory function que crea un PersonalizedAgent con acceso
    al contexto musical completo del usuario.
    """
    # Crea la herramienta de contexto del usuario
    get_context_tool = create_get_user_context_tool(token_info)

    # Formatea el prompt con el mensaje del usuario
    formatted_prompt = PERSONALIZED_PROMPT.format(
        user_message=user_message
    )

    # Crea el agente con la herramienta
    personalized_agent = LlmAgent(
        name="PersonalizedAgent",
        model="gemini-2.5-pro",
        instruction=formatted_prompt,
        description="Researches user's favorite music from their library.",
        tools=[get_context_tool],
        output_key=output_key
    )

    return personalized_agent
