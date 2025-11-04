# agents/orchestrator.py
"""
OrchestratorAgent: Coordina la búsqueda paralela de música nueva
y personalizada, y luego combina los resultados en la cola de Spotify.

Arquitectura:
    SequentialAgent(
        ParallelAgent(ScoutAgent, PersonalizedAgent),
        MergerAgent
    )
"""
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from agents.tools import SpotifyToolSet
from agents.scout_agent import create_scout_agent
from agents.personalized_agent import create_personalized_agent
from agents.prompts import MERGER_AGENT_PROMPT


def create_orchestrator_agent(
    token_info: dict,
    user_id: str,
    user_profile_str: str,
    queue_str: str,
    user_message: str
) -> SequentialAgent:
    """
    Crea el agente orquestador que coordina toda la pipeline.
    
    Args:
        token_info: Token de autenticación de Spotify del usuario
        user_id: ID del usuario
        user_profile_str: Perfil del usuario formateado como string
        queue_str: Cola actual de reproducción formateada como string
        user_message: Mensaje/petición del usuario
    
    Returns:
        SequentialAgent configurado con sub-agentes
    """
    # 1. Crear sub-agentes de búsqueda con output_keys
    scout_agent = create_scout_agent(
        user_message=user_message,
        output_key="scout_results"
    )
    
    personalized_agent = create_personalized_agent(
        token_info=token_info,
        user_message=user_message,
        output_key="personalized_results"
    )
    
    # 2. Crear ParallelAgent para ejecutar ambas búsquedas simultáneamente
    parallel_agent = ParallelAgent(
        name="ParallelSearchAgent",
        sub_agents=[scout_agent, personalized_agent],
        description="Ejecuta búsquedas de música nueva y favoritas en paralelo"
    )
    
    # 3. Crear MergerAgent para combinar resultados y agregar a cola
    spotify_toolset = SpotifyToolSet(token_info)
    
    formatted_prompt = MERGER_AGENT_PROMPT.format(
        user_id=user_id,
        user_profile_str=user_profile_str,
        queue_str=queue_str,
        user_message=user_message
    )
    
    merger_agent = LlmAgent(
        name="MergerAgent",
        model="gemini-2.5-pro",
        instruction=formatted_prompt,
        description="Combina resultados de búsquedas y agrega a cola Spotify",
        tools=spotify_toolset.get_tools()
    )
    
    # 4. Crear SequentialAgent que ejecuta búsquedas paralelas → merger
    orchestrator = SequentialAgent(
        name="OrchestratorAgent",
        sub_agents=[parallel_agent, merger_agent],
        description="Coordina búsquedas paralelas y síntesis de resultados"
    )
    
    return orchestrator
