import os
import logging
from anthropic import Anthropic
from dotenv import load_dotenv
from pl_stats.api_client import fetch_player_by_name, PlayerNotFoundError, APIQuotaError



load_dotenv()
log = logging.getLogger(__name__)

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))

SYSTEM_PROMPT = """You are a Premier League football analyst assistant.
You have access to real ESPN player data for Premier League players and provide
clear, engaging analysis for football fans.

When given player data, you:
- Summarise the player's profile and current season performance
- Highlight standout statistics and what they mean in context
- Give a pundit-style verdict on their season
- Keep responses under 200 words unless the user asks for more detail
- Use a confident, accessible tone — like a knowledgeable football commentator

Never make up statistics. Only use the data explicitly provided to you.
If certain stats are missing, acknowledge it and work with what you have."""



def _format_player_for_prompt(data: dict) -> str:
    """Format the merged player dict into a readable block for Claude."""
    stats = data.get("stats", {})


    stats_lines = "\n".join(
        f"  {k.replace('_', ' — ')}: {v}"
        for k, v in stats.items()
        if v not in (None, "", 0, "0.0")
    ) or "  No detailed stats available"


    return f"""
Player Profile:
  Name: {data.get('name')}
  Age: {data.get('age')} | DOB: {data.get('dob')}
  Nationality: {data.get('nationality')}
  Height: {data.get('height')} | Weight: {data.get('weight')}
  Position: {data.get('position')}
  Team: {data.get('team')}
  League: {data.get('league')}

Current Season Statistics:
{stats_lines}
""".strip()


def analyze_player(player_name: str, conversation_history: list[dict]) -> dict:
    """
    Resolve player name → fetch ESPN data → send to Claude → return analysis.

    Returns:
        {
            "reply": str,         # Claude's natural language analysis
            "player_data": dict,  # Full merged player data for frontend card
            "player_name": str,
        }
    """

    player_data = fetch_player_by_name(player_name)
    player_block = _format_player_for_prompt(player_data)

    messages = list(conversation_history)

    user_content = (
        f"Here is the current data for {player_data['name']}:\n\n"
        f"{player_block}\n\n"
        f"Please give me an analysis of this player."
    )

    if messages and messages[-1]["role"] == "user":
        messages[-1]["content"] += f"\n\n{user_content}"
    else:
        messages.append({"role": "user", "content": user_content})

    log.info(f"Sending {player_data['name']} data to Claude...")

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    reply = response.content[0].text
    log.info(f"Claude analysis complete for {player_data['name']}")

    return {
        "reply":       reply,
        "player_data": player_data,
        "player_name": player_data["name"],
    }