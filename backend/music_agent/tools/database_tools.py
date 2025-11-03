import sqlite3
from google.adk.tools import FunctionTool

DATABASE_PATH = "backend/data_spotify/spotify.sqlite"

def query_database(query: str) -> str:
    """Queries the Spotify database and returns the result."""
    try:
        con = sqlite3.connect(DATABASE_PATH)
        cur = con.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        con.close()
        return str(rows)
    except Exception as e:
        return f"Error querying database: {e}"

database_tools = [
    FunctionTool(query_database),
]
