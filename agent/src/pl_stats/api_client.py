import os
import logging
import requests
from dotenv import load_dotenv
from pl_stats.cache import get_cached_player, set_cached_player, record_api_call

load_dotenv()
log = logging.getLogger(__name__)

RAPIDAPI_KEY  = os.getenv("RAPIDAPI_KEY", "")
RAPIDAPI_HOST = "english-premiere-league1.p.rapidapi.com"
BASE_URL      = "https://english-premiere-league1.p.rapidapi.com"

HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": RAPIDAPI_HOST,
}

# ESPN team IDs for all 20 current Premier League clubs
PL_TEAM_IDS = {
    "Bournemouth":    "349",
    "Arsenal":        "359",
    "Aston Villa":    "362",
    "Brentford":      "337",
    "Brighton":       "331",
    "Chelsea":        "363",
    "Crystal Palace": "384",
    "Everton":        "368",
    "Fulham":         "370",
    "Liverpool":      "364",
    "Man City":       "382",
    "Man United":     "360",
    "Newcastle":      "361",
    "Nottm Forest":   "393",
    "Spurs":          "367",
    "West Ham":       "371",
    "Wolves":         "380",
}


class PlayerNotFoundError(Exception):
    pass


class APIQuotaError(Exception):
    pass


def _get(endpoint: str, params: dict = {}) -> dict:
    """Make a GET request, enforce quota, raise on HTTP errors."""
    try:
        record_api_call()
    except RuntimeError as e:
        raise APIQuotaError(str(e))

    try:
        resp = requests.get(
            f"{BASE_URL}{endpoint}",
            headers=HEADERS,
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.Timeout:
        raise RuntimeError(f"Request to {endpoint} timed out.")
    except requests.HTTPError as e:
        raise RuntimeError(f"API error on {endpoint}: {e.response.status_code}")


def _parse_athlete(athlete: dict) -> dict:
    """
    Parse a single athlete object from the roster response into a clean flat dict.
    Stats are embedded directly inside the athlete under statistics.splits.categories.
    """
    # Flatten stats from categories → stats array
    flat_stats = {}
    categories = (
        athlete
        .get("statistics", {})
        .get("splits", {})
        .get("categories", [])
    )
    for category in categories:
        cat_name = category.get("shortDisplayName", category.get("name", ""))
        for stat in category.get("stats", []):
            label = stat.get("shortDisplayName") or stat.get("abbreviation") or stat.get("name", "")
            value = stat.get("displayValue", "")
            if label and value not in ("", None):
                flat_stats[f"{cat_name} — {label}"] = value

    return {
        "id":          athlete.get("id"),
        "name":        athlete.get("fullName") or athlete.get("displayName"),
        "first_name":  athlete.get("firstName"),
        "last_name":   athlete.get("lastName"),
        "age":         athlete.get("age"),
        "dob":         athlete.get("dateOfBirth", "").split("T")[0],
        "nationality": athlete.get("citizenship"),
        "height":      athlete.get("displayHeight"),
        "weight":      athlete.get("displayWeight"),
        "jersey":      athlete.get("jersey"),
        "position":    athlete.get("position", {}).get("displayName"),
        "photo":       athlete.get("flag"),       # country flag — headshot not in roster
        "slug":        athlete.get("slug"),
        "stats":       flat_stats,
        "league":      "Premier League",
    }


def _fetch_roster(team_id: str) -> list[dict]:
    """Fetch and return the athletes list for a given team ID."""
    data = _get("/team/roster", {"teamId": team_id})
    return data.get("athletes", [])


def fetch_player_by_name(name: str) -> dict:
    """
    Search all PL team rosters for a player matching the given name.
    Stats are embedded in the roster response — no extra API calls needed.
    Result is cached per player name for 1 hour.

    Raises PlayerNotFoundError if no match is found across all squads.
    """
    cache_key = f"epl:{name.lower().strip()}"
    cached = get_cached_player(cache_key)
    if cached:
        return cached

    name_lower = name.lower().strip()
    log.info(f"Searching all PL rosters for '{name}'...")

    for team_name, team_id in PL_TEAM_IDS.items():
        log.info(f"Checking {team_name} roster...")
        try:
            athletes = _fetch_roster(team_id)
        except APIQuotaError:
            raise
        except Exception as e:
            log.warning(f"Could not fetch {team_name} roster: {e}")
            continue

        for athlete in athletes:
            full_name  = (athlete.get("fullName") or athlete.get("displayName") or "").lower()
            short_name = (athlete.get("shortName") or "").lower()
            slug       = (athlete.get("slug") or "").lower().replace("-", " ")

            # Match on full name, short name, or slug
            if (
                name_lower in full_name or
                full_name in name_lower or
                name_lower in short_name or
                name_lower in slug
            ):
                result = _parse_athlete(athlete)
                # Attach the team name since it's not in the athlete object
                result["team"] = team_name
                log.info(f"Found '{name}' → {result['name']} at {team_name}")
                set_cached_player(cache_key, result)
                return result

    raise PlayerNotFoundError(
        f"Could not find '{name}' in any Premier League squad. "
        "Check the spelling or try their full name (e.g. 'Mohamed Salah')."
    )