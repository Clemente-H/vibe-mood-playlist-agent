import spotipy

def curate_music(token_info: dict, prompt: str) -> list[str]:
    """
    Curates music based on a prompt and returns a list of Spotify track URIs.

    Args:
        token_info: The user's Spotify token information.
        prompt: The music recommendation prompt from the MoodAnalysisAgent.

    Returns:
        A list of Spotify track URIs.
    """

    # Create a Spotipy client
    sp = spotipy.Spotify(auth=token_info["access_token"])

    # For now, we'll return a hardcoded list of tracks
    # In the next step, we'll implement the Spotify search

    # Example search query based on the prompt
    # The prompt from the MoodAnalysisAgent will be more detailed
    search_query = prompt.split("find music that is ")[-1]

    try:
        results = sp.search(q=search_query, type="track", limit=10)
        track_uris = [track["uri"] for track in results["tracks"]["items"]]
        return track_uris
    except Exception as e:
        print(f"Error searching for tracks: {e}")
        return []
