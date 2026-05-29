import pytest
from unittest.mock import patch
from pl_stats.api_client import (
    fetch_player_by_name,
    PlayerNotFoundError,
    _parse_athlete,
)

MOCK_ATHLETE = {
    "id": "196876",
    "firstName": "Mohamed",
    "lastName": "Salah",
    "fullName": "Mohamed Salah",
    "displayName": "Mohamed Salah",
    "shortName": "M. Salah",
    "slug": "mohamed-salah",
    "age": 32,
    "dateOfBirth": "1992-06-15T07:00Z",
    "citizenship": "Egypt",
    "displayHeight": "5' 9\"",
    "displayWeight": "159 lbs",
    "jersey": "11",
    "position": {"displayName": "Forward"},
    "flag": "https://a.espncdn.com/i/teamlogos/countries/500/egy.png",
    "statistics": {
        "splits": {
            "categories": [
                {
                    "name": "general",
                    "shortDisplayName": "General",
                    "stats": [
                        {
                            "shortDisplayName": "G",
                            "displayValue": "18"
                        },
                        {
                            "shortDisplayName": "A",
                            "displayValue": "9"
                        },
                    ]
                }
            ]
        }
    }
}

MOCK_ROSTER_RESPONSE = {"athletes": [MOCK_ATHLETE]}
EMPTY_ROSTER_RESPONSE = {"athletes": []}


def test_parse_athlete_returns_correct_fields():
    result = _parse_athlete(MOCK_ATHLETE)
    assert result["name"] == "Mohamed Salah"
    assert result["nationality"] == "Egypt"
    assert result["position"] == "Forward"
    assert result["age"] == 32
    assert "General — G" in result["stats"]
    assert result["stats"]["General — G"] == "18"


def test_parse_athlete_flattens_stats():
    result = _parse_athlete(MOCK_ATHLETE)
    assert isinstance(result["stats"], dict)
    assert len(result["stats"]) == 2


@patch("pl_stats.api_client._fetch_roster")
def test_fetch_player_by_name_success(mock_roster):
    mock_roster.return_value = [MOCK_ATHLETE]
    result = fetch_player_by_name("Salah")
    assert result["name"] == "Mohamed Salah"
    assert result["nationality"] == "Egypt"
    assert result["stats"]["General — G"] == "18"


@patch("pl_stats.api_client._fetch_roster")
def test_fetch_player_not_found(mock_roster):
    mock_roster.return_value = []
    with pytest.raises(PlayerNotFoundError):
        fetch_player_by_name("NotARealPlayer99")


@patch("pl_stats.api_client._fetch_roster")
def test_fetch_player_uses_cache_on_second_call(mock_roster):
    mock_roster.return_value = [MOCK_ATHLETE]
    fetch_player_by_name("Mohamed Salah")
    fetch_player_by_name("Mohamed Salah")
    # Roster should only be fetched once — second call hits cache
    assert mock_roster.call_count == 1