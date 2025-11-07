import logging
import warnings
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.orchestrator import create_orchestrator_agent
from agents.context_formatter import (
    format_for_merger_agent,
    format_queue_info
)

# Suppress Google ADK warnings about non-text parts in responses
logging.getLogger('google.genai').setLevel(logging.ERROR)
warnings.filterwarnings('ignore', message='.*non-text parts.*')

# Agent Manager - Main API for agent execution
# Provides run_agent_with_context() function to execute the orchestrator
# pipeline with user context and return playlist results.


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
    # Format context using centralized formatter
    user_profile_str = format_for_merger_agent(
        spotify_context["user_profile"]
    )
    queue_str = format_queue_info(spotify_context["queue"])
    
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
    agent_outputs = {
        "scout_results": None,
        "personalized_results": None,
        "merger_input": None,
        "final_playlist": None
    }
    
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=content
    ):
        # Store event for debugging
        all_events.append({
            "author": event.author,
            "content": str(event.content.parts[0]) if event.content and event.content.parts else "No content"
        })
        
        # Capture output from each agent
        if event.content and event.content.parts:
            for part in event.content.parts:
                # Check for text content (agent outputs)
                if hasattr(part, 'text') and part.text:
                    if event.author == "ScoutAgent":
                        agent_outputs["scout_results"] = part.text
                    elif event.author == "PersonalizedAgent":
                        agent_outputs["personalized_results"] = part.text
                    elif event.author == "MergerAgent":
                        agent_outputs["merger_input"] = part.text
                
                # Look for MergerAgent's return_playlist_to_queue response
                if (hasattr(part, 'function_response') and
                        part.function_response):
                    if (part.function_response.name ==
                            'return_playlist_to_queue'):
                        playlist_result = dict(
                            part.function_response.response
                        )
                        agent_outputs["final_playlist"] = playlist_result
        
        # Break when orchestrator finishes
        if event.is_final_response() and event.author == "OrchestratorAgent":
            break
    
    # Print detailed analysis
    print("\n" + "="*80)
    print("DETAILED AGENT OUTPUTS ANALYSIS")
    print("="*80)
    
    # ScoutAgent output
    print("\n🔍 SCOUT AGENT OUTPUT:")
    print("-" * 80)
    if agent_outputs["scout_results"]:
        scout_lines = agent_outputs["scout_results"].strip().split('\n')
        print(f"Total lines: {len(scout_lines)}")
        print(f"First 5 URIs:")
        for line in scout_lines[:5]:
            print(f"  {line}")
        if len(scout_lines) > 5:
            print(f"  ... and {len(scout_lines) - 5} more")
    else:
        print("  ❌ NO OUTPUT from ScoutAgent")
    
    # PersonalizedAgent output
    print("\n👤 PERSONALIZED AGENT OUTPUT:")
    print("-" * 80)
    if agent_outputs["personalized_results"]:
        personalized_lines = agent_outputs["personalized_results"].strip().split('\n')
        print(f"Total lines: {len(personalized_lines)}")
        print(f"First 10 URIs:")
        for line in personalized_lines[:10]:
            print(f"  {line}")
        if len(personalized_lines) > 10:
            print(f"  ... and {len(personalized_lines) - 10} more")
    else:
        print("  ❌ NO OUTPUT from PersonalizedAgent")
    
    # MergerAgent analysis
    print("\n🔀 MERGER AGENT ANALYSIS:")
    print("-" * 80)
    if agent_outputs["final_playlist"]:
        final_uris = agent_outputs["final_playlist"].get("playlist", [])
        print(f"Total tracks in final playlist: {len(final_uris)}")
        
        # Check which tracks came from which agent
        scout_uris = set()
        personalized_uris = set()
        
        if agent_outputs["scout_results"]:
            scout_uris = set(agent_outputs["scout_results"].strip().split('\n'))
        
        if agent_outputs["personalized_results"]:
            personalized_uris = set(agent_outputs["personalized_results"].strip().split('\n'))
        
        from_scout = [uri for uri in final_uris if uri in scout_uris]
        from_personalized = [uri for uri in final_uris if uri in personalized_uris]
        unknown = [uri for uri in final_uris if uri not in scout_uris and uri not in personalized_uris]
        
        print(f"\n📊 Distribution:")
        print(f"  • From ScoutAgent: {len(from_scout)} tracks ({len(from_scout)/len(final_uris)*100:.1f}%)")
        print(f"  • From PersonalizedAgent: {len(from_personalized)} tracks ({len(from_personalized)/len(final_uris)*100:.1f}%)")
        if unknown:
            print(f"  • Unknown origin: {len(unknown)} tracks")
        
        if from_personalized:
            print(f"\n✅ PersonalizedAgent contributions:")
            for uri in from_personalized[:5]:
                print(f"    {uri}")
            if len(from_personalized) > 5:
                print(f"    ... and {len(from_personalized) - 5} more")
        else:
            print(f"\n❌ NO tracks from PersonalizedAgent were selected by MergerAgent!")
    else:
        print("  ❌ NO FINAL PLAYLIST generated")
    
    print("\n" + "="*80)
    
    # Return the playlist result or empty dict if none found
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