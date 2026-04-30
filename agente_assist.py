from langchain_ollama import ChatOllama
from langchain.agents import create_agent

from tools import (
    get_game_info,
    get_player_info,
    suggest_similar_games,
    search_steam_games,
    duckduckgo_tool
)


def build_agent():
    llm = ChatOllama(
        model="llama3.2",
        base_url="http://localhost:11434",
        temperature=0,
    )

    tools = [
        get_game_info,
        get_player_info,
        suggest_similar_games,
        search_steam_games,
        duckduckgo_tool
    ]

    SYSTEM_PROMPT = """You are SteamGuide, a helpful Steam assistant.
Always use tools when needed and never show tool calls."""

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )

    return agent