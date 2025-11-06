import logging
import warnings
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.orchestrator import create_orchestrator_agent

# Suppress Google ADK warnings about non-text parts in responses
logging.getLogger('google.genai').setLevel(logging.ERROR)
warnings.filterwarnings('ignore', message='.*non-text parts.*')

# Agent Manager - Main API for agent execution
# Provides run_agent_with_context() function to execute the orchestrator
# pipeline with user context and return playlist results.


def _format_context_for_prompt(spotify_context: dict) -> tuple[str, str]:
    """
    Formats the user profile and queue into strings for LLM prompts.
    
    Returns:
        tuple: (profile_str, queue_str)
        - profile_str: Brief summary for MergerAgent
        - queue_str: Current playback queue
    """
    user_profile = spotify_context["user_profile"]
    
    # Format brief profile summary (for MergerAgent)
    profile_str = "- Top Artists: " + ", ".join([artist['name'] for artist in user_profile.get("top_artists", [])[:5]])
    profile_str += "\n- Top Genres: " + ", ".join(list(set(genre for artist in user_profile.get("top_artists", []) for genre in artist["genres"][:2])))
    profile_str += "\n- Recently Played: " + ", ".join([track['name'] for track in user_profile.get("recently_played", [])[:5]])

    # Format queue
    queue_str = "- Currently Playing: "
    if spotify_context["queue"] and spotify_context["queue"].get("currently_playing"):
        queue_str += f"{spotify_context['queue']['currently_playing']['name']} by {spotify_context['queue']['currently_playing']['artists'][0]['name']}\n"
    else:
        queue_str += "Nothing\n"
    
    queue_str += "- Up Next: "
    if spotify_context["queue"] and spotify_context["queue"].get("queue"):
        queue_str += ", ".join([item["name"] for item in spotify_context["queue"]["queue"][:5]])
    else:
        queue_str += "Empty"

    return profile_str, queue_str


async def run_agent_with_context(
    user_message: str,
    spotify_context: dict,
    user_id: str
) -> dict:
    """
    Runs the orchestrator agent with Google ADK using the official
    Runner pattern.
    
    Args:
        user_message: User's request/message
        spotify_context: Dict with 'user_profile' and 'queue'
        user_id: Spotify user ID
    
    Returns:
        dict with playlist and metadata from MergerAgent
    """
    # Format context for prompts
    user_profile_str, queue_str = _format_context_for_prompt(spotify_context)
    
    # Get full user context
    user_context = spotify_context["user_profile"]
    
    # Create orchestrator agent
    orchestrator = create_orchestrator_agent(
        user_context=user_context,
        user_id=user_id,
        user_profile_str=user_profile_str,
        queue_str=queue_str,
        user_message=user_message
    )
    
    # Setup session service and runner
    session_service = InMemorySessionService()
    
    APP_NAME = "vibe-mood-playlist-agent"
    USER_ID = f"spotify_{user_id}"
    SESSION_ID = f"session_{user_id}"
    
    # Create session
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    
    # Create runner
    runner = Runner(
        agent=orchestrator,
        app_name=APP_NAME,
        session_service=session_service
    )
    
    # Prepare user message
    content = types.Content(
        role='user',
        parts=[types.Part(text=user_message)]
    )
    
    # Execute and collect results
    playlist_result = None
    all_events = []
    
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=content
    ):
        all_events.append(f"{event.author}: {event.content.parts[0] if event.content and event.content.parts else 'No content'}")
        
        # Look for MergerAgent's return_playlist_to_queue response
        if event.content and event.content.parts:
            for part in event.content.parts:
                if (hasattr(part, 'function_response') and
                        part.function_response):
                    if (part.function_response.name ==
                            'return_playlist_to_queue'):
                        playlist_result = dict(
                            part.function_response.response
                        )
        
        # Break when orchestrator finishes
        if event.is_final_response() and event.author == "OrchestratorAgent":
            break
    
    # Debug: print all events if no playlist
    if not playlist_result:
        print("\n[DEBUG] All events:")
        for e in all_events:
            print(f"  {e}")    # Return the playlist result or empty dict if none found
    return playlist_result if playlist_result else {
        "status": "error",
        "message": "No playlist generated"
    }


# Old implementation (commented for reference)
# async def run_agent_with_context(user_message: str, spotify_context: dict) -> dict:
#     """
#     Runs the music agent with a given user message and spotify context.
#     """
    
#     user_profile_str, queue_str = _format_context_for_prompt(spotify_context)

#     # Format the main prompt with the gathered context
#     formatted_prompt = MAIN_AGENT_PROMPT.format(
#         user_profile_str=user_profile_str,
#         queue_str=queue_str,
#         user_message=user_message
#     )

#     print("--- PROMPT SENT TO AGENT ---")
#     print(formatted_prompt)
#     print("-----------------------------")

#     # Call the agent, which returns a streaming async generator
#     response_parts = []
#     async for part in root_agent.run_async(formatted_prompt):
#         response_parts.append(part)
    
#     agent_response_str = "".join(response_parts)

#     # TODO: Add robust JSON parsing and validation
#     import json
#     try:
#         agent_plan = json.loads(agent_response_str)
#     except json.JSONDecodeError:
#         print("Error: Agent did not return valid JSON.")
#         agent_plan = {"error": "Invalid JSON response from agent", "raw_response": agent_response_str}

#     return agent_plan