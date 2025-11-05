from google.adk.agents import Agent

# This is the main orchestrator agent.
# For now, it is a simple agent that will receive the formatted prompt.
# In the future, it could be a more complex agent that calls specialist sub-agents.

root_agent = Agent(
    name="OrchestratorAgent",
    # We can add personality, instructions, etc. here later
)
