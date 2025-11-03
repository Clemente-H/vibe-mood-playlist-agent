from google.adk.agents.llm_agent import Agent
from .tools.spotify_tools import spotify_tools
from .tools.database_tools import database_tools

all_tools = spotify_tools + database_tools

root_agent = Agent(
    model='gemini-1.5-flash',
    name='music_agent',
    description='A music agent that can find songs and add them to a Spotify queue.',
    instruction='You are a music assistant. Your goal is to find a song and add it to the user\'s queue. \n\n1. First, use the query_database tool to find relevant songs from the local database. \n2. Then, use the search_track tool to find the song on Spotify and get its URI. \n3. Finally, use the add_to_queue tool to add the song to the user\'s queue.',
    tools=all_tools,
)
