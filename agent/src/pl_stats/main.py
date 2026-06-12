import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from pl_stats.agent import analyse_player
from pl_stats.api_client import PlayerNotFoundError, APIQuotaError
from pl_stats.cache import get_call_count

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ── Prometheus metrics ─────────────────────────────────────────
chat_requests_total = Counter(
    "plstats_chat_requests_total",
    "Total number of chat requests",
    ["status"]   # labels: success, not_found, quota_exceeded, error
)

chat_response_seconds = Histogram(
    "plstats_chat_response_seconds",
    "Chat endpoint response time in seconds",
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

api_calls_gauge = Gauge(
    "plstats_rapidapi_calls_today",
    "Number of RapidAPI calls made today"
)

cache_hits_total = Counter(
    "plstats_cache_hits_total",
    "Number of player lookups served from cache"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("PL Stats AI Agent starting up...")
    yield
    log.info("PL Stats AI Agent shutting down.")


app = FastAPI(
    title="PL Stats AI Agent",
    description="English Premier League player stats + AI analysis via chat",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response models ──────────────────────────────────
class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    player_name: str
    conversation_history: list[Message] = []


class ChatResponse(BaseModel):
    reply: str
    player_data: dict
    player_name: str
    api_calls_today: int


# ── Routes ─────────────────────────────────────────────────────
@app.get("/health")
def health():
    calls = get_call_count()
    api_calls_gauge.set(calls)
    return {"status": "healthy", "api_calls_today": calls}


@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    api_calls_gauge.set(get_call_count())
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.player_name.strip():
        raise HTTPException(status_code=400, detail="player_name cannot be empty.")

    history = [m.model_dump() for m in request.conversation_history]
    start_time = time.time()

    try:
        result = analyse_player(request.player_name.strip(), history)
        duration = time.time() - start_time

        chat_requests_total.labels(status="success").inc()
        chat_response_seconds.observe(duration)
        api_calls_gauge.set(get_call_count())

        log.info(f"Chat request completed in {duration:.2f}s for '{request.player_name}'")

        return ChatResponse(
            reply=result["reply"],
            player_data=result["player_data"],
            player_name=result["player_name"],
            api_calls_today=get_call_count(),
        )

    except PlayerNotFoundError as e:
        chat_requests_total.labels(status="not_found").inc()
        raise HTTPException(status_code=404, detail=str(e))
    except APIQuotaError as e:
        chat_requests_total.labels(status="quota_exceeded").inc()
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        chat_requests_total.labels(status="error").inc()
        log.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Something went wrong. Please try again.")