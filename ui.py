import gradio as gr
import re
from agente_assist import build_agent
from steam_api import search_games

CURRENT_GAMES = []
# Inicializar agente
agent = build_agent()


# ---------- UI helpers ----------

def format_price(price):
    if not price:
        return ""

    if price.lower() == "free":
        return '<span style="color:#66c0f4; font-weight:bold;">Free</span>'

    if price == "Check on Steam":
        return '<span style="color:#888;">Check on Steam</span>'

    return f'<span style="color:#a4d007;">{price}</span>'

def format_tags(tags):
    if not tags:
        return ""

    return "".join(
        [f'<span class="tag">{tag}</span>' for tag in tags[:4]]
    )

def format_price_block(game):
    price = game.get("price", "")
    original = game.get("original_price", "")
    discount = game.get("discount", 0)

    if price.lower() == "free":
        return '<span style="color:#66c0f4; font-weight:bold;">Free</span>'

    if discount > 0:
        return f"""
        <div>
            <span style="color:#a4d007; font-weight:bold;">-{discount}%</span><br>
            <span style="text-decoration:line-through; color:#888;">{original}</span><br>
            <span style="color:#a4d007;">{price}</span>
        </div>
        """

    if price:
        return f'<span style="color:#a4d007;">{price}</span>'

    return '<span style="color:#888;">Check on Steam</span>'


def format_rating(game):
    rating = game.get("rating", "")
    count = game.get("rating_count", 0)

    if not rating:
        return ""

    return f"""
    <div style="color:#66c0f4; font-size:12px;">
        {rating} ({count})
    </div>
    """

def game_card(game):

    return f"""
    <a href="{game.get('url')}" target="_blank"
    style="text-decoration:none; color:white;">

        <div class="game-card">

            <img src="{game.get('image')}" class="game-image" />

            <div class="game-info">

                <h3>{game.get('name')}</h3>

                <div class="tags">
                    {format_tags(game.get("tags", []))}
                </div>

                <div class="price">
                    {game.get('price')}
                </div>

            </div>

        </div>

    </a>
    """

wishlist_state = gr.State([])

wishlist_box = gr.HTML()

from db import add_to_wishlist, load_wishlist, remove_from_wishlist


def add_game_to_wishlist(game):
    wishlist = add_to_wishlist(game)
    return render_wishlist(wishlist), wishlist


def remove_game_from_wishlist(game_id):
    wishlist = remove_from_wishlist(game_id)
    return render_wishlist(wishlist), wishlist

def render_wishlist(wishlist):
    if not wishlist:
        return "<p>No games in wishlist</p>"

    html = '<div style="display:flex; gap:10px; flex-wrap:wrap;">'

    for game in wishlist:
        html += f"""
        <div style="background:#1b2838; padding:10px; width:180px;">
            <img src="{game['image']}" style="width:100%;" />
            <p>{game['name']}</p>
            <button onclick="removeGame('{game['id']}')">❌ Remove</button>
        </div>
        """

    html += "</div>"
    return html


def render_store(query):
    games = search_games(query)

    # strict match
    filtered_games = [
        g for g in games
        if query.lower() in g["name"].lower()
    ]

    # 🔥 fallback if too few results
    if len(filtered_games) < 3:
        filtered_games = games  # show broader results

    if not filtered_games:
        return "<p>No matching games found.</p>"

    cards = "".join([game_card(g) for g in filtered_games[:4]])

    return f"""
    <div style="display:flex; gap:15px; flex-wrap:wrap;">
        {cards}
    </div>
    """


# ---------- Chat logic ----------
def extract_games_from_text(text):
    games = []

    # Match numbered list: "1. Game Name"
    matches = re.findall(r"\d+\.\s+\*\*(.*?)\*\*", text)

    # fallback if no bold (**Game**)
    if not matches:
        matches = re.findall(r"\d+\.\s+([A-Za-z0-9 :\-™]+)", text)

    return matches

def render_main_game(query):
    games = search_games(query)

    if not games:
        return ""

    main_game = games[0]

    return f"""
    <h3 style="color:#66c0f4;">🎮 Your Search</h3>
    <div style="display:flex; gap:15px;">
        {game_card(main_game)}
    </div>
    """

def render_games_list(game_names):

    all_games = []

    added = set()

    valid_count = 0

    for name in game_names:

        results = search_games(name)

        if not results:
            continue

        best_match = None

        for g in results:

            if is_good_match(name, g["name"]):

                # 🚫 avoid duplicates
                if g["name"] in added:
                    continue

                best_match = g
                break

        # skip invalid
        if not best_match:
            best_match = results[0] if results else None
        # save game
        added.add(best_match["name"])

        all_games.append(best_match)

        valid_count += 1

        # ✅ stop only after 5 VALID cards
        if valid_count >= 5:
            break

    if not all_games:
        return "<p>No matching games found.</p>"

    cards = "".join([game_card(g) for g in all_games])

    return f"""
    <div style="
        display:flex;
        gap:15px;
        flex-wrap:wrap;
    ">
        {cards}
    </div>
    """

def is_good_match(query, game_name):
    query = query.lower()
    game_name = game_name.lower()

    # remove symbols
    query = re.sub(r"[^\w\s]", "", query)
    game_name = re.sub(r"[^\w\s]", "", game_name)

    return query in game_name or game_name in query

def extract_text(user_message):
    if isinstance(user_message, str):
        return user_message

    if isinstance(user_message, list):
        texts = [m.get("text", "") for m in user_message if m.get("type") == "text"]
        return " ".join(texts)

    return ""


def clean_query(user_message):
    text = extract_text(user_message)
    return text.strip()





def get_bot_response(history):
    # history já vem no formato correto (messages)
    messages = history.copy() if history else []

    result = agent.invoke({"messages": messages})

    return result["messages"][-1].content


def user_submit(message, history):
    history = history or []

    history.append({
        "role": "user",
        "content": message
    })

    return "", history


def bot_response(history):
    user_message = history[-1]["content"]

    bot_message = get_bot_response(history)
    print("+", user_message)

    query = clean_query(user_message)

    main_games = search_games(query)

    global CURRENT_GAMES

    CURRENT_GAMES = main_games.copy()


    # 🎮 MAIN GAME (always)
    main_html = render_main_game(query)

    # 🤖 AI recommendations
    game_names = extract_games_from_text(bot_message)

    recommended_games = []

    recommended_games = game_names

    CURRENT_GAMES.extend(recommended_games)

    if game_names:
        rec_html = """
        <h3 style="color:#66c0f4;">🎯 Recommended Games</h3>
        """ + render_games_list(game_names)
    else:
        rec_html = ""

    # ✅ combine both
    store_html = main_html + rec_html

    history.append({
        "role": "assistant",
        "content": bot_message
    })

    all_games = list(dict.fromkeys(game_names))

    wishlist_games = load_wishlist()

    wishlist_names = [g["name"] for g in wishlist_games]

    wishlist_html = render_wishlist(wishlist_games)

    return (
        history,
        store_html,
        wishlist_html,
        gr.update(choices=all_games, value=None),
        gr.update(choices=wishlist_names, value=None)
    )

# ---------- CSS ----------

steam_css = """
body {
    background: #0f1923;
}

.gradio-container {
    background:
        linear-gradient(180deg, #1b2838 0%, #0f1923 100%);
    color: #ffffff;
    font-family: Arial, sans-serif;
}

/* HEADER */

#header {
    text-align: center;
    padding: 20px;
    font-size: 42px;
    font-weight: bold;
    color: #66c0f4;

    text-shadow: 0 0 15px rgba(102,192,244,0.5);
}

/* CARDS */

.game-card {

    background: #16202d;

    border-radius: 14px;

    overflow: hidden;

    width: 240px;

    transition: all 0.25s ease;

    box-shadow:
        0 4px 15px rgba(0,0,0,0.4);

    border: 1px solid rgba(255,255,255,0.05);
}

.game-card:hover {

    transform: translateY(-6px) scale(1.02);

    box-shadow:
        0 12px 25px rgba(0,0,0,0.5);

    border: 1px solid #66c0f4;
}

/* IMAGE */

.game-image {
    width: 100%;
    height: 120px;
    object-fit: cover;
}

/* CONTENT */

.game-info {
    padding: 14px;
}

.game-info h3 {
    color: #ffffff;
    margin-bottom: 10px;
    font-size: 18px;
}

/* TAGS */

.tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 12px;
}

.tag {
    background: #22394f;
    color: #66c0f4;
    padding: 4px 8px;
    border-radius: 8px;
    font-size: 12px;
}

/* PRICE */

.price {
    color: #a4d007;
    font-weight: bold;
    font-size: 20px;
}

/* BUTTONS */

button {

    border-radius: 10px !important;

    transition: 0.2s !important;

    font-weight: bold !important;
}

button:hover {
    transform: scale(1.03);
}

/* INPUT */

textarea, input {

    background: #16202d !important;

    border: 1px solid #2a475e !important;

    color: white !important;

    border-radius: 10px !important;
}
"""


# ---------- UI ----------
def add_selected_to_wishlist(game_name):

    if not game_name:
        return render_wishlist(load_wishlist())

    games = search_games(game_name)

    if games:
        add_to_wishlist(games[0])

    updated_wishlist = render_wishlist(load_wishlist())

    return updated_wishlist

def remove_selected_from_wishlist(game_name):

    wishlist = load_wishlist()

    # find matching game
    for game in wishlist:
        if game["name"] == game_name:
            remove_from_wishlist(game["id"])
            break

    updated = load_wishlist()

    names = [g["name"] for g in updated]

    return (
        render_wishlist(updated),
        gr.update(choices=names, value=None)
    )

def build_ui():

    with gr.Blocks(title="SteamGuide Assistant") as demo:

        gr.Markdown("""
        <div style='text-align:center; padding:20px;'>

        <h1 style='font-size:48px; color:#66c0f4;'>
        SteamGuide
        </h1>

        <p style='font-size:18px; color:#c7d5e0;'>
        Discover your next favorite game with AI-powered recommendations.
        </p>

        </div>
        """)

        gr.Markdown('<div id="header">🎮 SteamGuide Assistant</div>')

        # 🔥 MAIN LAYOUT
        with gr.Row():

            # LEFT SIDE
            with gr.Column(scale=3):

                chatbot = gr.Chatbot(
                    height=650,
                    render_markdown=True
                )

                # 💬 INPUT
                msg = gr.Textbox(
                    placeholder="Ask about games...",
                    show_label=False
                )

                with gr.Row():
                    send = gr.Button("Send 🎮")
                    clear = gr.Button("🗑️ Clear Chat")

            # RIGHT SIDE
            with gr.Column(scale=2):

                gr.Markdown("## 🎮 Games")
                store = gr.HTML()

                gr.Markdown("## ❤️ Wishlist")

                wishlist_selector = gr.Dropdown(
                    choices=[],
                    label="Select a game to add"
                )

                add_wishlist_btn = gr.Button(
                    "❤️ Add to Wishlist"
                )

                remove_selector = gr.Dropdown(
                    choices=[],
                    label="Remove a game"
                )

                remove_wishlist_btn = gr.Button(
                    "❌ Remove"
                )

                wishlist = gr.HTML(
                    value=render_wishlist(load_wishlist())
                )

        # 🔥 SEND BUTTON
        send.click(
            user_submit,
            [msg, chatbot],
            [msg, chatbot]
        ).then(
            bot_response,
            [chatbot],
            [
                chatbot,
                store,
                wishlist,
                wishlist_selector,
                remove_selector
            ]
        )

        # 🔥 ENTER KEY
        msg.submit(
            user_submit,
            [msg, chatbot],
            [msg, chatbot]
        ).then(
            bot_response,
            [chatbot],
            [
                chatbot,
                store,
                wishlist,
                wishlist_selector,
                remove_selector
            ]
        )

        # ❤️ ADD TO WISHLIST
        add_wishlist_btn.click(
            fn=add_selected_to_wishlist,
            inputs=[wishlist_selector],
            outputs=[wishlist]
        )

        # ❌ REMOVE FROM WISHLIST
        remove_wishlist_btn.click(
            fn=remove_selected_from_wishlist,
            inputs=[remove_selector],
            outputs=[wishlist, remove_selector]
        )

        # 🗑️ CLEAR CHAT
        clear.click(lambda: [], None, chatbot)

    demo.launch(css=steam_css, server_name="localhost")

    return demo
