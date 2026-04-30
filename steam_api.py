import requests


# ---------- Helpers ----------
def get_user_country():
    try:
        res = requests.get("http://ip-api.com/json/")
        data = res.json()
        return data.get("countryCode", "PT")  # fallback
    except:
        return "PT"

USER_COUNTRY = get_user_country()



# ---------- Main function ----------

def get_game_details(game_id):
    url = f"https://store.steampowered.com/api/appdetails?appids={game_id}&cc={USER_COUNTRY}&l=english"

    try:
        res = requests.get(url)
        data = res.json()
        return data.get(str(game_id), {}).get("data", {})
    except Exception as e:
        print("Details API error:", e)
        return {}



def search_games(query):
    url = "https://store.steampowered.com/api/storesearch/"

    params = {
        "term": query,
        "l": "english",
        "cc": USER_COUNTRY
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
    except Exception as e:
        print("Steam API error:", e)
        return []

    games = []

    for item in data.get("items", [])[:6]:
        game_id = item.get("id")

        if not game_id:
            continue

        # 🔥 Get full details
        details = get_game_details(game_id)

        # 🎯 PRICE + DISCOUNT
        price = "Check on Steam"
        original_price = ""
        discount = 0

        if details.get("is_free"):
            price = "Free"

        elif details.get("price_overview"):
            po = details["price_overview"]

            price = po.get("final_formatted", "Check on Steam")
            original_price = po.get("initial_formatted", "")
            discount = po.get("discount_percent", 0)

        # 🎯 TAGS (genres)
        tags = [g["description"] for g in details.get("genres", [])] if details else []

        # ⭐ RATINGS (based on number of reviews)
        rating = ""
        rating_count = 0

        if details.get("recommendations"):
            rating_count = details["recommendations"].get("total", 0)

        if rating_count > 50000:
            rating = "Overwhelmingly Positive"
        elif rating_count > 10000:
            rating = "Very Positive"
        elif rating_count > 2000:
            rating = "Positive"
        elif rating_count > 500:
            rating = "Mixed"

        game = {
            "id": game_id,
            "name": item.get("name", "Unknown"),

            # 🔥 Better image
            "image": details.get("header_image", item.get("tiny_image", "")),

            "price": price,
            "original_price": original_price,
            "discount": discount,

            "rating": rating,
            "rating_count": rating_count,

            "url": f"https://store.steampowered.com/app/{game_id}",
            "tags": tags
        }

        games.append(game)

    return games