# agents/tools.py
"""
Herramientas (Tools) para los agentes del sistema.
Incluye herramientas de búsqueda y control de Spotify.
"""
from google.adk.tools import FunctionTool as Tool
from data_spotify.database_service import search_all_songs
import spotify_service
from typing import List


class SpotifyToolSet:
    """
    Esta clase contiene el token_info del usuario y expone
    las funciones del servicio de Spotify como Herramientas del ADK.
    """
    def __init__(self, token_info: dict):
        self.token_info = token_info

    def get_tools(self) -> List[Tool]:
        """Retorna una lista de todas las herramientas de Spotify."""
        token = self.token_info  # Captura del closure
        
        @Tool
        def search_track_tool(query: str) -> dict:
            """
            Busca una canción en Spotify usando una consulta de texto.
            Retorna una lista de resultados de canciones.
            """
            return spotify_service.search_track(token, query)

        @Tool
        def add_to_queue_tool(song_uri: str) -> dict:
            """
            Agrega una canción a la cola de reproducción del usuario.
            Necesita el 'song_uri' (Spotify URI) de la canción.
            Ejemplo de URI: 'spotify:track:123456...
            """
            return spotify_service.add_to_queue(token, song_uri)

        @Tool
        def start_playback_tool() -> dict:
            """
            Inicia o reanuda la reproducción en el dispositivo
            activo del usuario.
            """
            return spotify_service.start_playback(token)

        @Tool
        def pause_playback_tool() -> dict:
            """
            Pausa la reproducción en el dispositivo activo
            del usuario.
            """
            return spotify_service.pause_playback(token)

        @Tool
        def next_track_tool() -> dict:
            """
            Salta a la siguiente canción en la cola.
            """
            return spotify_service.next_track(token)
        
        @Tool
        def create_playlist_tool(playlist_name: str) -> dict:
            """
            Crea una nueva playlist de Spotify a partir de la cola
            actual del usuario.
            """
            return spotify_service.create_playlist_from_queue(
                token, playlist_name
            )
        
        return [
            search_track_tool,
            add_to_queue_tool,
            start_playback_tool,
            pause_playback_tool,
            next_track_tool,
            create_playlist_tool
        ]


# --- Herramientas de Búsqueda para Sub-Agentes ---

@Tool
def search_local_db_by_mood(mood_params: dict, limit: int) -> dict:
    """
    Busca en la base de datos local de canciones usando parámetros de audio.

    Args:
        mood_params: Diccionario con parámetros de audio (energy, valence,
                    danceability, acousticness, etc.)
        limit: Número máximo de canciones a retornar

    Returns:
        dict con lista de canciones encontradas
    """
    results = search_all_songs(mood_params, None, limit)
    return {"results": results}


def create_get_user_context_tool(token_info: dict):
    """
    Factory function que crea una herramienta para obtener el contexto
    musical completo del usuario desde Spotify.
    
    Args:
        token_info: Token de autenticación de Spotify
    
    Returns:
        Tool configurado con acceso al token del usuario
    """
    @Tool
    def get_user_music_context() -> dict:
        """
        Obtiene el contexto musical completo del usuario desde Spotify:
        - Top 50 canciones más escuchadas
        - Artistas favoritos
        - Géneros preferidos
        - Playlists del usuario
        
        Retorna toda esta información para seleccionar las canciones
        más apropiadas según el mood solicitado.
        """
        user_context = spotify_service.get_user_context(token_info)
        
        if "error" in user_context:
            return {"error": user_context["error"]}
        
        return {
            "top_tracks": user_context.get("top_tracks", []),
            "top_artists": user_context.get("top_artists", []),
            "top_genres": user_context.get("top_genres", []),
            "recently_played": user_context.get("recently_played", []),
            "playlists": user_context.get("playlists", []),
            "total_tracks": len(user_context.get("top_tracks", [])),
            "total_playlists": len(user_context.get("playlists", []))
        }
    
    return get_user_music_context
