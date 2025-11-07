"""
Test script for real Google ADK agent execution using Runner pattern.
Following official Google ADK documentation pattern.
"""

import asyncio
import logging
import sys
import warnings
from pathlib import Path

# Suppress all warnings including Google ADK non-text parts warnings
warnings.filterwarnings('ignore')
logging.getLogger('google.genai').setLevel(logging.ERROR)
logging.getLogger('google.genai.generative_models').setLevel(logging.ERROR)
logging.getLogger('google').setLevel(logging.ERROR)

# Add backend directory to path if running from root
current_dir = Path(__file__).parent
if current_dir.name == "backend":
    # Running from backend directory
    sys.path.insert(0, str(current_dir))
    env_path = current_dir.parent / ".env"
else:
    # Running from root directory
    backend_dir = current_dir / "backend"
    sys.path.insert(0, str(backend_dir))
    env_path = current_dir / ".env"

from dotenv import load_dotenv

# Import our agent factory
from agents.agent_manager import run_agent_with_context
from agents.context_formatter import (
    format_for_merger_agent,
    format_queue_info
)

# Import Spotify service for authentication
import spotify_service


async def test_real_agents_with_runner():
    """Test real Google ADK agents using the official Runner pattern."""
    
    print("=" * 80)
    print("TESTING REAL GOOGLE ADK AGENTS WITH RUNNER")
    print("=" * 80)
    
    # Load environment variables
    load_dotenv(dotenv_path=env_path)
    print(f"[OK] Loading .env from: {env_path}")
    print(f"[OK] .env exists: {env_path.exists()}")
    
    # Change to backend directory for Spotify cache
    original_cwd = Path.cwd()
    backend_dir = Path(__file__).parent
    import os
    os.chdir(backend_dir)
    print(f"[OK] Working directory: {Path.cwd()}")
    
    # Step 1: Authenticate with Spotify
    print("\n1. Authenticating with Spotify...")
    oauth = spotify_service.get_spotify_oauth()
    
    # Using cached token from previous runs
    token_info = oauth.get_cached_token()
    if not token_info:
        print("Error: No cached token found. Please run authentication first.")
        os.chdir(original_cwd)  # Restore original directory
        return
    
    print("[OK] Token retrieved successfully")
    
    # Get user info for context
    import spotipy
    sp = spotipy.Spotify(auth=token_info["access_token"])
    user_info = sp.current_user()
    user_id = user_info["id"]
    display_name = user_info.get('display_name', 'Unknown')
    print(f"[OK] Authenticated as: {display_name} ({user_id})")
    
    # Step 2: Get user profile and queue
    print("\n2. Fetching user profile and current queue...")
    user_context = spotify_service.get_user_context(token_info)
    queue = spotify_service.get_current_queue(token_info)
    
    # Prepare spotify_context in the format expected by agent_manager
    spotify_context = {
        "user_profile": user_context,
        "queue": queue
    }
    
    # ANALYZE CONTEXT
    print("\n   📊 USER CONTEXT STATS:")
    print(f"      • Top Artists: {len(user_context.get('top_artists', []))}")
    print(f"      • Top Tracks: {len(user_context.get('top_tracks', []))}")
    print(f"      • Recently Played: {len(user_context.get('recently_played', []))}")
    print(f"      • Playlists: {len(user_context.get('playlists', []))}")
    
    # Count tracks in playlists
    total_playlist_tracks = 0
    for playlist in user_context.get('playlists', []):
        tracks = playlist.get('tracks', [])
        total_playlist_tracks += len(tracks)
    
    print(f"      • Total tracks in playlists: {total_playlist_tracks}")
    total_available = total_playlist_tracks + len(user_context.get('top_tracks', [])) + len(user_context.get('recently_played', []))
    print(f"      • TOTAL TRACKS AVAILABLE FOR PERSONALIZEDAGENT: {total_available}")
    
    # Use centralized context formatters
    user_profile_str = format_for_merger_agent(user_context)
    queue_str = format_queue_info(queue)
    print(user_profile_str)
    
    # Context size analysis
    total_chars = len(user_profile_str) + len(queue_str)
    estimated_tokens = total_chars / 4
    print(f"\n   📝 FORMATTED CONTEXT:")
    print(f"      • Characters: {total_chars}")
    print(f"      • Estimated tokens: ~{int(estimated_tokens)}")
    
    print(f"\n   🤖 AGENT DISTRIBUTION:")
    print(f"      • ScoutAgent: Searches 8M+ songs (no user context)")
    print(f"      • PersonalizedAgent: Searches {total_available} user tracks")
    print(f"      • MergerAgent: Combines 40% personalized + 60% scout")
    
    # Show sample
    print(f"\n   📋 CONTEXT PREVIEW (first 500 chars):")
    print("   " + "-" * 76)
    for line in user_profile_str[:500].split('\n'):
        print(f"   {line}")
    print("   ...")
    print("   " + "-" * 76)
    
    user_message = "Quiero full reggaeton para una fiesta"
    
    print(f"\n[OK] Context ready for agents")
    print(f"[OK] Queue: {queue_str[:80]}...")

    # Step 3: Run agent with context
    print("\n3. Running agent with context...")
    user_message = "Quiero rock alternativo para estudiar tranquilo"
    print(f'Query: "{user_message}"')
    
    print("\n" + "=" * 80)
    print("AGENT EXECUTION OUTPUT")
    print("=" * 80 + "\n")
    
    # Run the agent
    result = await run_agent_with_context(
        user_message=user_message,
        spotify_context=spotify_context,
        user_id=user_id
    )
    
    print("\n" + "=" * 80)
    print("FINAL RESULT")
    print("=" * 80)
    print(f"\nResult: {result}")
    
    # Step 4: Verify Spotify queue (optional)
    print("\n4. Verifying Spotify queue...")
    try:
        import spotipy
        sp = spotipy.Spotify(auth=token_info["access_token"])
        
        # Get current queue
        current_queue = sp.queue()
        
        if current_queue and "queue" in current_queue:
            queue_tracks = current_queue["queue"]
            print(f"[OK] Current queue has {len(queue_tracks)} tracks")
            
            # Show first 10 tracks in queue
            print("\n  First 10 tracks in queue:")
            for i, track in enumerate(queue_tracks[:10], 1):
                track_name = track.get("name", "Unknown")
                artists = track.get("artists", [])
                artist_name = artists[0]["name"] if artists else "Unknown"
                print(f"    {i}. {track_name} - {artist_name}")
        else:
            print("  [WARNING] Queue is empty or unavailable")
            
    except Exception as e:
        print(f"  [WARNING] Error checking queue: {e}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETED SUCCESSFULLY")
    print("=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(test_real_agents_with_runner())
    except KeyboardInterrupt:
        print("\n[WARNING] Test interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
