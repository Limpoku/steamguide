import gradio as gr
import re
from agente_assist import build_agent
from steam_api import search_games

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

    return " ".join([
        f'<span style="background:#1b2838; padding:3px 6px; margin:2px; border-radius:5px; font-size:12px;">{tag}</span>'
        for tag in tags[:3]
    ])

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
    <a href="{game.get('url', '#')}" target="_blank" style="text-decoration:none;">
        <div style="
            background:#2a475e;
            padding:10px;
            border-radius:10px;
            width:200px;
            transition: transform 0.2s;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        "
        onmouseover="this.style.transform='scale(1.05)'"
        onmouseout="this.style.transform='scale(1)'"
        >

            <img src="{game['image']}" style="width:100%; border-radius:8px;" />

            <h4 style="color:#66c0f4;">{game['name']}</h4>

            <div>{format_rating(game)}</div>

            <div>{format_price_block(game)}</div>

            <div style="margin-top:5px;">
                {format_tags(game.get('tags', []))}
            </div>

        </div>
    </a>
    """


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

    for name in game_names:
        results = search_games(name)

        if not results:
            continue

        best_match = None

        for g in results:
            if is_good_match(name, g["name"]):
                best_match = g
                break

        # 🚨 IMPORTANT: skip instead of fallback
        if not best_match:
            continue

        all_games.append(best_match)

    if not all_games:
        return "<p>No matching games found.</p>"

    cards = "".join([game_card(g) for g in all_games[:5]])

    return f"""
    <div style="display:flex; gap:15px; flex-wrap:wrap;">
        {cards}
    </div>
    """

def is_good_match(query, game_name):
    q_words = set(query.lower().split())
    g_words = set(re.findall(r'\w+', game_name.lower()))

    # require ALL words from query to exist as full words
    return q_words.issubset(g_words)

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

    # 🎮 MAIN GAME (always)
    main_html = render_main_game(query)

    # 🤖 AI recommendations
    game_names = extract_games_from_text(bot_message)

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

    return history, store_html

# ---------- CSS ----------

steam_css = """
body { background-color: #1b2838; }
.gradio-container {
    background: linear-gradient(180deg, #1b2838 0%, #171a21 100%);
    color: #c7d5e0;
}
#header {
    text-align: center;
    padding: 15px;
    font-size: 28px;
    font-weight: bold;
    color: #66c0f4;
}
"""


# ---------- UI ----------

def build_ui():
    with gr.Blocks(title="SteamGuide Assistant") as demo:

        gr.Markdown('<div id="header">🎮 SteamGuide Assistant</div>')

        chatbot = gr.Chatbot(
            height=450,
            #type="messages",
            render_markdown=True
        )

        gr.Markdown("### 🎮 Games")
        store = gr.HTML()

        msg = gr.Textbox(
            placeholder="Ask about games...",
            show_label=False
        )

        send = gr.Button("Send 🎮")
        clear = gr.Button("🗑️ Clear Chat")

        # interações
        send.click(user_submit, [msg, chatbot], [msg, chatbot]) \
            .then(bot_response, chatbot, [chatbot, store])

        msg.submit(user_submit, [msg, chatbot], [msg, chatbot]) \
            .then(bot_response, chatbot, [chatbot, store])

        clear.click(lambda: [], None, chatbot)

    demo.launch(css=steam_css, server_name="localhost")

    return demo