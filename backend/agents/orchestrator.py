# agents/orchestrator.py
"""
OrchestratorAgent: Coordinates parallel search for new music and personalized
recommendations, then combines results into a Spotify queue.

Architecture:
    SequentialAgent(
        ParallelAgent(ScoutAgent, PersonalizedAgent),
        MergerAgent
    )

Includes the return_playlist_to_queue tool used exclusively by MergerAgent.
"""
from typing import List

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.tools import FunctionTool as Tool

from agents.personalized_agent import create_personalized_agent
from agents.prompts import MERGER_AGENT_PROMPT
from agents.scout_agent import create_scout_agent


@Tool
def return_playlist_to_queue(playlist: List[str]) -> dict:
    """
    Returns the final list of selected song URIs.
    This is the final output of the MergerAgent that will be processed
    by the chat endpoint to add songs to Spotify.

    Args:
        playlist: List of Spotify URIs (e.g., ["spotify:track:123", ...])

    Returns:
        dict with playlist and metadata
    """
    return {
        "status": "success",
        "playlist": playlist,
        "total_tracks": len(playlist),
        "message": f"Playlist created with {len(playlist)} songs"
    }


def create_orchestrator_agent(
    user_context: dict,
    user_id: str,
    user_profile_str: str,
    queue_str: str,
    user_message: str
) -> SequentialAgent:
    """
    Creates the orchestrator agent that coordinates the entire pipeline.
    
    Args:
        user_context: Complete user context (top_tracks, playlists, etc.)
        user_id: User ID
        user_profile_str: User profile summary for MergerAgent
        queue_str: Current playback queue formatted as string
        user_message: User's request/message
    
    Returns:
        SequentialAgent configured with sub-agents
    """
    # 1. Create search sub-agents with output_keys
    scout_agent = create_scout_agent(
        user_message=user_message,
        output_key="scout_results"
    )
    
    personalized_agent = create_personalized_agent(
        user_context=user_context,
        user_message=user_message,
        output_key="personalized_results"
    )
    
    # 2. Create ParallelAgent with both agents
    parallel_agent = ParallelAgent(
        name="ParallelSearchAgent",
        sub_agents=[scout_agent, personalized_agent],
        description="Executes music search from database and user library in parallel"
    )
    
    # 3. Create MergerAgent to combine results and return playlist
    formatted_prompt = MERGER_AGENT_PROMPT.format(
        user_id=user_id,
        user_profile_str=user_profile_str,
        user_message=user_message
    )
    
    merger_agent = LlmAgent(
        name="MergerAgent",
        model="gemini-2.5-flash",
        instruction=formatted_prompt,
        description="Combines search results and returns final playlist",
        tools=[return_playlist_to_queue]
    )
    
    # 4. Create SequentialAgent that executes parallel searches → merger
    orchestrator = SequentialAgent(
        name="OrchestratorAgent",
        sub_agents=[parallel_agent, merger_agent],
        description="Coordinates parallel searches and synthesis of results"
    )
    
    return orchestrator
