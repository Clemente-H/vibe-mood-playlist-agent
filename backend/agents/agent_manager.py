# agent_manager.py
from agents.orchestrator import create_orchestrator_agent
import spotipy


def _format_context_for_prompt(spotify_context: dict) -> tuple[str, str]:
    """
    Formatea el perfil de usuario y la cola en un string para
    el prompt del LLM.
    """
    
    # Tu lógica de formato de perfil (¡está muy bien!)
    profile_str = ""
    if spotify_context.get("user_profile"):
        profile_data = spotify_context["user_profile"]
        profile_str += "- Top Artists: " + ", ".join([
            artist['name']
            for artist in profile_data.get("top_artists", [])[:5]
        ])
        profile_str += "\n- Top Genres: " + ", ".join(list(set(
            genre
            for artist in profile_data.get("top_artists", [])
            for genre in artist["genres"][:2]
        )))
        profile_str += "\n- Recently Played: " + ", ".join([
            track['name']
            for track in profile_data.get("recently_played", [])[:5]
        ])
    else:
        profile_str = "No disponible."

    # Tu lógica de formato de cola (¡también muy bien!)
    queue_str = ""
    queue_check = (
        spotify_context.get("queue") and
        not spotify_context["queue"].get("error")
    )
    if queue_check:
        queue_data = spotify_context["queue"]
        
        queue_str = "- Currently Playing: "
        if queue_data.get("currently_playing"):
            curr_track = queue_data['currently_playing']
            queue_str += (
                f"{curr_track['name']} by "
                f"{curr_track['artists'][0]['name']}\n"
            )
        else:
            queue_str += "Nothing\n"
        
        queue_str += "- Up Next: "
        if queue_data.get("queue"):
            queue_str += ", ".join([
                item["name"]
                for item in queue_data["queue"][:5]
            ])
        else:
            queue_str += "Empty"
    else:
        queue_str = "No disponible."

    return profile_str, queue_str


async def run_agent_with_context(
    user_message: str,
    spotify_context: dict,
    token_info: dict
) -> str:
    """
    Ejecuta el agente de música con un mensaje de usuario y el
    contexto de Spotify.
    """
    
    user_profile_str, queue_str = _format_context_for_prompt(
        spotify_context
    )

    # Obtener el user_id del token de Spotify
    sp = spotipy.Spotify(auth=token_info["access_token"])
    user_id = sp.current_user()["id"]

    # 1. Crea el agente orquestador (¡ahora le pasas el token!)
    orchestrator_agent = create_orchestrator_agent(
        token_info=token_info,
        user_id=user_id,
        user_profile_str=user_profile_str,
        queue_str=queue_str,
        user_message=user_message
    )

    print("--- CONTEXTO ENVIADO AL ORQUESTADOR ---")
    print(f"User Profile:\n{user_profile_str}")
    print(f"Queue:\n{queue_str}")
    print("---------------------------------------")

    # 2. Ejecuta el agente con generate_content_stream
    # Esta es la forma correcta de ejecutar un agente en Google ADK
    response_parts = []
    
    # Usar el método run() síncronamente y luego convertir a async
    # O mejor, usar directamente generate_content si está disponible
    try:
        # Intentar ejecutar con el modelo directamente
        async for chunk in orchestrator_agent.model.generate_content_stream_async(
            user_message
        ):
            if hasattr(chunk, 'text'):
                response_parts.append(chunk.text)
    except Exception as e:
        print(f"Error usando generate_content_stream: {e}")
        # Fallback: intentar con un approach más simple
        result = orchestrator_agent.model.generate_content(user_message)
        response_parts.append(result.text)
    
    final_response = "".join(response_parts)

    print("--- RESPUESTA FINAL DEL AGENTE ---")
    print(final_response)
    print("----------------------------------")

    # 3. Retorna la respuesta final en lenguaje natural
    return final_response

