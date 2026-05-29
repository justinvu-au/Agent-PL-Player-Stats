import time
import logging
from cachetools import TTLCache


log = logging.getLogger(__name__)

# Cap 200 players, each entry lives 1 hour
_player_cache: TTLCache = TTLCache(maxsize=200, ttl=3600)

_call_log: list[float] = []
DAILY_LIMIT = 90

def get_cached_player(key: str) -> dict | None:
    result = _player_cache.get(key)
    if result:
        log.info(f"Cache HIT for '{key}'")
    return result


def set_cached_player(key: str, data: dict) -> None:
    _player_cache[key] = data
    log.info(f"Cache set for '{key}' - {len(_player_cache)} entries in cache")


def record_api_call() -> None:
    now = time.time()
    _call_log.append(now)
    cutoff = now - 86400   #remove calls more than 24 hours
    _call_log[:] = [t for t in _call_log if t > cutoff]
    calls_today = len(_call_log)
    log.info(f"API calls today: {calls_today}/{DAILY_LIMIT}")
    if calls_today >= DAILY_LIMIT:
        raise RuntimeError(
            f"Daily API quota nearly exhausted ({calls_today} calls). "
            "Try again tomorrow or upgrade your RapidAPI plan."
        )


def get_call_count() -> int:
    cutoff = time.time() - 86400
    return len([t for t in _call_log if t > cutoff])


