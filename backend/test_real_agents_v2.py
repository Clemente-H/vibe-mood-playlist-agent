"""
Test script for real Google ADK agent execution using Runner pattern.
Following official Google ADK documentation pattern.
"""

import os
import asyncio
from dotenv import load_dotenv
from google.genai import types

# Import Google ADK components
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

# Import our agent factory
from agents.orchestrator import create_orchestrator_agent

# Import Spotify service for authentication
import spotify_service


async def test_real_agents_with_runner():
    """Test real Google ADK agents using the official Runner pattern."""
    
    print("=" * 80)
    print("TESTING REAL GOOGLE ADK AGENTS WITH RUNNER")
    print("=" * 80)
    
    # Load environment variables
    load_dotenv()
    
    # Step 1: Authenticate with Spotify
    print("\n1. Authenticating with Spotify...")
    oauth = spotify_service.get_spotify_oauth()
    
    # Using cached token from previous runs
    token_info = oauth.get_cached_token()
    if not token_info:
        print("Error: No cached token found. Please run authentication first.")
        return
    
    print(f"✓ Token retrieved successfully")
    
    # Get user info for context
    import spotipy
    sp = spotipy.Spotify(auth=token_info["access_token"])
    user_info = sp.current_user()
    user_id = user_info["id"]
    print(f"✓ Authenticated as: {user_info.get('display_name', 'Unknown')} ({user_id})")
    
    # Step 2: Get user profile and queue
    print("\n2. Fetching user profile and current queue...")
    user_context = spotify_service.get_user_context(token_info)
    queue = spotify_service.get_current_queue(token_info)
    
    # Format user profile
    top_tracks = user_context.get('top_tracks', [])[:5]
    user_profile_str = f"Top 5 tracks: {', '.join([t['name'] for t in top_tracks])}"
    
    # Format queue
    queue_items = queue.get('queue', [])[:5]
    queue_str = f"Current queue: {', '.join([q['name'] for q in queue_items])}"
    
    user_message = "Recomiéndame canciones energéticas para bailar"
    
    print(f"✓ User profile: {user_profile_str[:80]}...")
    print(f"✓ Queue: {queue_str[:80]}...")
    
    # Step 3: Create the orchestrator agent
    print("\n3. Creating OrchestratorAgent...")
    orchestrator = create_orchestrator_agent(
        token_info=token_info,
        user_id=user_id,
        user_profile_str=user_profile_str,
        queue_str=queue_str,
        user_message=user_message
    )
    print(f"✓ Agent created: {orchestrator.name}")
    print(f"  - Type: {type(orchestrator).__name__}")
    print(f"  - Sub-agents: {len(orchestrator.sub_agents)}")
    
    # Step 3: Setup Session Service and Runner (OFFICIAL PATTERN)
    print("\n3. Setting up SessionService and Runner...")
    
    # Create session service (in-memory for testing)
    session_service = InMemorySessionService()
    
    # Define session identifiers
    APP_NAME = "vibe-mood-playlist-agent"
    USER_ID = f"spotify_{user_id}"
    SESSION_ID = "test_session_001"
    
    # Create session
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print(f"✓ Session created: {SESSION_ID}")
    
    # Create Runner (THIS IS THE KEY!)
    runner = Runner(
        agent=orchestrator,
        app_name=APP_NAME,
        session_service=session_service
    )
    print(f"✓ Runner created for agent '{orchestrator.name}'")
    
    # Step 4: Execute agent with user query
    print("\n4. Executing agent with query...")
    user_query = "Recomiéndame canciones energéticas para bailar"
    print(f"Query: \"{user_query}\"")
    
    # Prepare user message in ADK format
    content = types.Content(
        role='user',
        parts=[types.Part(text=user_query)]
    )
    
    # Execute using runner.run_async (OFFICIAL PATTERN)
    print("\n" + "=" * 80)
    print("AGENT EXECUTION OUTPUT")
    print("=" * 80 + "\n")
    
    final_response_text = "Agent did not produce a final response."
    events_count = 0
    
    # Iterate through events yielded by runner.run_async
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=content
    ):
        events_count += 1
        
        # Log event details
        print(f"\n[Event {events_count}] Author: {event.author}")
        print(f"  is_final: {event.is_final_response()}")
        
        # Log intermediate events
        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    print(f"  Text: {part.text[:200]}...")
                elif hasattr(part, 'function_call') and part.function_call:
                    print(f"  Function Call: {part.function_call.name}")
                    print(f"    Args: {part.function_call.args}")
                elif hasattr(part, 'function_response') and part.function_response:
                    print(f"  Function Response: {part.function_response.name}")
                    response_str = str(part.function_response.response)[:300]
                    print(f"    Response: {response_str}...")
        
        # Check if this is the FINAL response from the ROOT agent (OrchestratorAgent)
        # Only break when the entire SequentialAgent pipeline is complete
        if event.is_final_response() and event.author == "OrchestratorAgent":
            print("  [FINAL RESPONSE FROM ORCHESTRATOR]")
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            break
        elif event.is_final_response():
            print(f"  [FINAL RESPONSE FROM SUB-AGENT: {event.author}]")
    
    print("\n" + "=" * 80)
    print("FINAL RESULT")
    print("=" * 80)
    print(f"\nTotal events processed: {events_count}")
    print(f"\nFinal Response:\n{final_response_text}")
    
    # Step 5: Verify session state changes
    print("\n5. Checking session state...")
    final_session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    
    if final_session:
        print(f"✓ Session has {len(final_session.events)} events")
        print(f"  State keys: {list(final_session.state.keys())}")
    
    # Step 6: Verify Spotify queue was actually updated
    print("\n6. Verifying Spotify queue was updated...")
    try:
        import spotipy
        sp = spotipy.Spotify(auth=token_info["access_token"])
        
        # Get current queue
        current_queue = sp.queue()
        
        if current_queue and "queue" in current_queue:
            queue_tracks = current_queue["queue"]
            print(f"✓ Current queue has {len(queue_tracks)} tracks")
            
            # Show first 10 tracks in queue
            print("\n  First 10 tracks in queue:")
            for i, track in enumerate(queue_tracks[:10], 1):
                track_name = track.get("name", "Unknown")
                artists = track.get("artists", [])
                artist_name = artists[0]["name"] if artists else "Unknown"
                print(f"    {i}. {track_name} - {artist_name}")
        else:
            print("  ⚠ Queue is empty or unavailable")
            
    except Exception as e:
        print(f"  ⚠ Error checking queue: {e}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETED SUCCESSFULLY")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_real_agents_with_runner())
