# agents/context_formatter.py
"""
Centralized context formatting for all agents.
Provides consistent formatting of user music context with different
detail levels for different agent needs.
"""


def format_for_personalized_agent(user_context: dict) -> str:
    """
    Formats user library for PersonalizedAgent with FULL DETAIL.
    
    PersonalizedAgent needs URIs to select specific tracks, so this
    format includes complete track information with URIs.
    
    Args:
        user_context: Processed user context dict
    
    Returns:
        Detailed string with all track URIs
    """
    lines = []
    
    # User's playlists with tracks (DETAILED with URIs)
    playlists = user_context.get("playlists", [])
    if playlists:
        lines.append("YOUR PLAYLISTS:")
        for playlist in playlists:
            tracks = playlist.get("tracks", [])
            if tracks:
                lines.append(f"  • {playlist['name']}:")
                # Show tracks with URIs (up to 30 per playlist)
                for track in tracks[:30]:
                    name = track.get("name", "Unknown")
                    artist = track.get("artist", "Unknown")
                    uri = track.get("uri", "")
                    lines.append(f"    - {name} by {artist} ({uri})")
    
    # Top tracks
    top_tracks = user_context.get("top_tracks", [])
    if top_tracks:
        lines.append("\nYOUR TOP TRACKS:")
        for track in top_tracks[:20]:
            name = track.get("name", "Unknown")
            artist = track.get("artist", "Unknown")
            uri = track.get("uri", "")
            lines.append(f"  • {name} by {artist} ({uri})")
    
    # Recently played
    recently = user_context.get("recently_played", [])
    if recently:
        lines.append("\nRECENTLY PLAYED:")
        for track in recently[:20]:
            name = track.get("name", "Unknown")
            artist = track.get("artist", "Unknown")
            uri = track.get("uri", "")
            lines.append(f"  • {name} by {artist} ({uri})")
    
    # Top artists for context
    top_artists = user_context.get("top_artists", [])
    if top_artists:
        lines.append("\nYOUR FAVORITE ARTISTS:")
        for artist in top_artists[:20]:
            name = artist.get("name", "Unknown")
            genres = ", ".join(artist.get("genres", [])[:3])
            lines.append(f"  • {name} ({genres})")
    
    return "\n".join(lines)


def format_for_merger_agent(user_context: dict) -> str:
    """
    Formats user profile for MergerAgent with COMPACT SUMMARY.
    
    MergerAgent only needs general context to make decisions,
    not individual URIs. This format is token-efficient.
    
    Args:
        user_context: Processed user context dict
    
    Returns:
        Compact string summary without URIs
    """
    profile_str = "### User's Music Profile\n\n"
    
    # Top Artists
    top_artists = user_context.get("top_artists", [])
    if top_artists:
        profile_str += "**Top Artists:**\n"
        for artist in top_artists[:5]:
            genres = ", ".join(artist.get("genres", [])[:2])
            profile_str += f"- {artist['name']} (Genres: {genres})\n"
        profile_str += "\n"
    
    # Top Tracks (compact - just names)
    top_tracks = user_context.get("top_tracks", [])
    if top_tracks:
        profile_str += "**Top Tracks (Last 6 Months):**\n"
        for track in top_tracks[:20]:
            name = track.get("name", "Unknown")
            artist = track.get("artist", "Unknown")
            profile_str += f"- {name} by {artist}\n"
        profile_str += "\n"
    
    # Recently Played (compact - just names)
    recently_played = user_context.get("recently_played", [])
    if recently_played:
        profile_str += "**Recently Played:**\n"
        for track in recently_played[:20]:
            name = track.get("name", "Unknown")
            artist = track.get("artist", "Unknown")
            profile_str += f"- {name} by {artist}\n"
        profile_str += "\n"
    
    # User's Playlists (COMPACT format - comma-separated track names)
    playlists = user_context.get("playlists", [])
    if playlists:
        profile_str += "**User's Playlists:**\n"
        for pl in playlists:
            tracks = pl.get("tracks", [])
            if tracks:
                # Compact: "Playlist: track1, track2, track3..."
                track_names = [t.get("name", "Unknown") for t in tracks[:30]]
                track_list = ", ".join(track_names)
                profile_str += f"- {pl['name']}: {track_list}\n"
            else:
                profile_str += f"- {pl['name']}: (empty)\n"
        profile_str += "\n"
    
    return profile_str


def format_queue_info(queue_data: dict) -> str:
    """
    Formats current playback queue information.
    
    Args:
        queue_data: Queue data from Spotify API
    
    Returns:
        Formatted queue string
    """
    queue_str = "### Current Playback Queue\n"
    
    # Currently playing
    if queue_data and queue_data.get("currently_playing"):
        current = queue_data["currently_playing"]
        artist_name = current["artists"][0]["name"]
        queue_str += f"**Currently Playing:** {current['name']} by {artist_name}\n"
    else:
        queue_str += "**Currently Playing:** Nothing\n"
    
    # Up next
    if queue_data and queue_data.get("queue"):
        queue_items = queue_data["queue"][:5]
        track_names = [item["name"] for item in queue_items]
        queue_str += "**Up Next:** " + ", ".join(track_names)
    else:
        queue_str += "**Up Next:** Empty"
    
    return queue_str
