from agents.prompts import MAIN_AGENT_PROMPT
from agents.orchestrator import root_agent

# This manager is responsible for the core agent logic.
# It prepares the prompt and runs the agent with the provided context.

def _format_context_for_prompt(spotify_context: dict) -> tuple[str, str]:
    """Formats the user profile and queue into a string for the LLM prompt."""
    
    # Format user profile
    profile_str = "- Top Artists: " + ", ".join([artist['name'] for artist in spotify_context["user_profile"].get("top_artists", [])[:5]])
    profile_str += "\n- Top Genres: " + ", ".join(list(set(genre for artist in spotify_context["user_profile"].get("top_artists", []) for genre in artist["genres"][:2]))) # Unique top genres
    profile_str += "\n- Recently Played: " + ", ".join([track['name'] for track in spotify_context["user_profile"].get("recently_played", [])[:5]])

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

async def run_agent_with_context(user_message: str, spotify_context: dict) -> dict:
    """
    Runs the music agent with a given user message and spotify context.
    """
    
    user_profile_str, queue_str = _format_context_for_prompt(spotify_context)

    # Format the main prompt with the gathered context
    formatted_prompt = MAIN_AGENT_PROMPT.format(
        user_profile_str=user_profile_str,
        queue_str=queue_str,
        user_message=user_message
    )

    print("--- PROMPT SENT TO AGENT ---")
    print(formatted_prompt)
    print("-----------------------------")

    # Call the agent, which returns a streaming async generator
    response_parts = []
    async for part in root_agent.run_async(formatted_prompt):
        response_parts.append(part)
    
    agent_response_str = "".join(response_parts)

    # TODO: Add robust JSON parsing and validation
    import json
    try:
        agent_plan = json.loads(agent_response_str)
    except json.JSONDecodeError:
        print("Error: Agent did not return valid JSON.")
        agent_plan = {"error": "Invalid JSON response from agent", "raw_response": agent_response_str}

    return agent_plan
