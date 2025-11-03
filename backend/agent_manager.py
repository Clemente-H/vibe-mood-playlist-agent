from prompts import MAIN_AGENT_PROMPT
from music_agent.agent import root_agent

# This manager is responsible for the core agent logic.
# It prepares the prompt and runs the agent with the provided context.

async def run_agent_with_context(user_message: str, spotify_context: dict) -> dict:
    """
    Runs the music agent with a given user message and spotify context.

    Args:
        user_message: The message from the user.
        spotify_context: A dictionary containing user profile data and queue information.

    Returns:
        A dictionary representing the agent's execution plan.
    """

    # TODO: Format the context into a string for the prompt
    user_profile_str = "..."
    queue_str = "..."

    # Format the main prompt with the gathered context
    formatted_prompt = MAIN_AGENT_PROMPT.format(
        user_genres="N/A", # Placeholder
        user_artists="N/A", # Placeholder
        queue_songs=queue_str, # Placeholder
        user_message=user_message
    )

    print("--- PROMPT SENT TO AGENT ---")
    print(formatted_prompt)
    print("-----------------------------")

    # Call the agent
    agent_plan = await root_agent.run_async(formatted_prompt)

    return agent_plan
