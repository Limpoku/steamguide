games_db = {
    "CP77": {
        "title": "Cyberpunk 2077",
        "genre": "RPG",
        "rating": 8.2,
        "image": "https://cdn.cloudflare.steamstatic.com/steam/apps/1091500/header.jpg"
    },
    "ER": {
        "title": "Elden Ring",
        "genre": "Action RPG",
        "rating": 9.5,
        "image": "https://cdn.cloudflare.steamstatic.com/steam/apps/1245620/header.jpg"
    }
}

players_db = {
    "76561198199403846": {
        "player_name": "Francisco",
        "player_age": 22,
        "favorite_games": ["Elden Ring", "Cyberpunk 2077"]
    }
}


def get_game(game_id):
    return games_db.get(game_id)


def get_player(steamid):
    return players_db.get(steamid)