import pytest
from unittest.mock import patch, MagicMock
from pl_stats.agent import analyze_player, _format_player_for_prompt

MOCK_PLAYER_DATA = {
    "id": "3109",
    "name": "Mohamed Salah",
    "age": 32,
    "dob": "1992-06-15",
    "nationality": "Egypt",
    "height": "5'9\"",
    "weight": "159 lbs",
    "position": "Forward",
    "team": "Liverpool",
    "photo": "https://example.com/salah.jpg",
    "stats": {
        "Scoring_G": "18",
        "Scoring_A": "9",
    },
    "league": "Premier League",
}


def test_format_player_for_prompt_contains_key_fields():
    result = _format_player_for_prompt(MOCK_PLAYER_DATA)
    assert "Mohamed Salah" in result
    assert "Liverpool" in result
    assert "Egypt" in result
    assert "18" in result


@patch("pl_stats.agent.fetch_player_by_name")
@patch("pl_stats.agent.client")
def test_analyse_player_returns_correct_shape(mock_client, mock_fetch):
    mock_fetch.return_value = MOCK_PLAYER_DATA

    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="Salah has been outstanding this season...")]
    mock_client.messages.create.return_value = mock_message

    result = analyze_player("Salah", [])

    assert result["player_name"] == "Mohamed Salah"
    assert "reply" in result
    assert "player_data" in result
    assert result["player_data"]["stats"]["Scoring_G"] == "18"