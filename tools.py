from langchain.tools import tool
from db import get_game, get_player
from steam_api import search_games
from langchain_community.tools import DuckDuckGoSearchResults

@tool
def get_game_info(game_id: str):
    """
    Retrieve information about a game using its ID.
    """

    game = get_game(game_id)

    if not game:
        return "❌ Game not found"

    return f"""
🎮 {game['title']}
Genre: {game['genre']}
Rating: ⭐ {game['rating']}
"""

@tool
def get_player_info(steamid: str):
    """
    Retrieves information about a player based on their Steam ID.
    """

    player = get_player(steamid)

    if not player:
        return "❌ Player not found"

    return f"""
🎮 Player Info:
- Name: {player['player_name']}
- Age: {player['player_age']}
- Favorite Games: {", ".join(player['favorite_games'])}
"""

@tool
def suggest_similar_games(game_id: str):
    """
    Suggest similar games based on a given game ID.
    """

    mapping = {
        "CP77": ["The Witcher 3", "Starfield"],
        "ER": ["Dark Souls 3", "Sekiro"]
    }

    return ", ".join(mapping.get(game_id, []))

@tool
def search_steam_games(query: str):
    """
    Search for games on Steam using a query.
    """

    games = search_games(query)

    if not games:
        return "No games found."

    result = "🎮 Steam Results:\n"

    for g in games:
        result += f"- {g['name']} ({g['price']})\n"

    return result

print("[INIT, A criar tool DuckDuckGoSearchResults...]")
duckduckgo_tool= DuckDuckGoSearchResults(
    name="duckduckgo_web_search",
    num_results= 5
)