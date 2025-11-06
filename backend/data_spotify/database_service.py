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
    
    Args:
        mood_params: Dict with audio features. Each feature can be:
                    - dict with 'min' and/or 'max': {"min": 0.7, "max": 1.0}
                    - float: treated as minimum value (backward compatible)
        genre: Optional genre filter
        limit: Maximum number of results
    """
    conn = get_db_connection()
    
    # Base query (construct uri from track_id since uri column doesn't exist)
    query = """
        SELECT 
            CAST(t.id AS VARCHAR) as track_id,
            CAST(t.name AS VARCHAR) as track_name,
            CAST(a.name AS VARCHAR) as artist_name,
            'spotify:track:' || CAST(t.id AS VARCHAR) as uri
        FROM tracks t
        JOIN r_track_artist rta ON t.id = rta.track_id
        JOIN artists a ON rta.artist_id = a.id
        JOIN audio_features af ON t.audio_feature_id = af.id
    """

    where_clauses = []
    params = []

    # Feature mapping: name -> SQL column
    feature_columns = {
        'energy': 'af.energy',
        'valence': 'af.valence',
        'danceability': 'af.danceability',
        'acousticness': 'af.acousticness',
        'instrumentalness': 'af.instrumentalness',
        'speechiness': 'af.speechiness',
        'tempo': 'af.tempo',
        'loudness': 'af.loudness'
    }

    for feature_name, column in feature_columns.items():
        if feature_name in mood_params:
            feature_value = mood_params[feature_name]
            
            # Handle dict with min/max
            if isinstance(feature_value, dict):
                if 'min' in feature_value and 'max' in feature_value:
                    where_clauses.append(
                        f"CAST({column} AS VARCHAR)::FLOAT BETWEEN ? AND ?"
                    )
                    params.append(feature_value['min'])
                    params.append(feature_value['max'])
                elif 'min' in feature_value:
                    where_clauses.append(
                        f"CAST({column} AS VARCHAR)::FLOAT >= ?"
                    )
                    params.append(feature_value['min'])
                elif 'max' in feature_value:
                    where_clauses.append(
                        f"CAST({column} AS VARCHAR)::FLOAT <= ?"
                    )
                    params.append(feature_value['max'])
            
            # Handle backward compatibility (float = minimum)
            elif isinstance(feature_value, (int, float)):
                where_clauses.append(f"CAST({column} AS VARCHAR)::FLOAT > ?")
                params.append(feature_value)
    
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
