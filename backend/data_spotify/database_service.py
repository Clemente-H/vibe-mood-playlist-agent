import duckdb
import os

# Define the path to the database file
DB_FILE = os.path.join(os.path.dirname(__file__), "spotify.sqlite")

def get_db_connection():
    """Establishes a connection to the DuckDB database."""
    return duckdb.connect(database=DB_FILE, read_only=True) # Read-only for querying

def search_all_songs(mood_params: dict, genre: str = None, limit: int = 20):
    """
    Searches the main tracks table for songs matching given audio features.
    This is the tool for the ScoutAgent.
    """
    conn = get_db_connection()
    
    # Base query
    query = """
        SELECT 
            CAST(t.id AS VARCHAR) as track_id,
            CAST(t.name AS VARCHAR) as track_name,
            CAST(a.name AS VARCHAR) as artist_name
        FROM tracks t
        JOIN r_track_artist rta ON t.id = rta.track_id
        JOIN artists a ON rta.artist_id = a.id
        JOIN audio_features af ON t.audio_feature_id = af.id
    """

    where_clauses = []
    params = []

    # Example mood mapping
    if mood_params.get('energy'):
        where_clauses.append("CAST(af.energy AS VARCHAR)::FLOAT > ?")
        params.append(mood_params['energy'])
    if mood_params.get('valence'):
        where_clauses.append("CAST(af.valence AS VARCHAR)::FLOAT > ?")
        params.append(mood_params['valence'])
    
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    query += f" ORDER BY CAST(t.popularity AS VARCHAR)::INT DESC LIMIT {limit}"

    print(f"--- DATABASE QUERY ---\n{query}\nParams: {params}\n---------------------")

    try:
        results = conn.execute(query, params).fetchdf()
        return results.to_dict('records')
    except Exception as e:
        print(f"Error querying database: {e}")
        return []
    finally:
        conn.close()

# --- Placeholder for user-specific table functions ---

def create_or_update_user_table(user_id: str, songs_data: list):
    """Creates or updates a user-specific table with their liked songs."""
    # TODO: Implement the logic to write to a user-specific table.
    # Connection needs to be read-write for this.
    print(f"(Placeholder) Would create/update table for user {user_id} with {len(songs_data)} songs.")
    pass

def search_liked_songs(user_id: str, mood_params: dict, limit: int = 10):
    """Searches the user-specific table. Tool for the PersonalizedAgent."""
    # TODO: Implement query logic for the user-specific table.
    print(f"(Placeholder) Would search liked songs for user {user_id} "
          f"with mood {mood_params}, limit={limit}.")
    return []
