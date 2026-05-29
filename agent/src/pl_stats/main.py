import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from pl_stats.agent import analyze_player
from pl_stats.api_client import PlayerNotFoundError, APIQuotaError
from pl_stats.cache import get_call_count




load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

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


@app.get("/health")
def health():
    return {"status": "healthy", "api_call_today": get_call_count()}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.player_name.strip():
        raise HTTPException(status_code=400, detail="player_name cannot be empty.")

    history = [m.model_dump() for m in request.conversation_history]

    try:
        result = analyze_player(request.player_name.strip(), history)
    except PlayerNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except APIQuotaError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Something went wrong. Please try again.")

    return ChatResponse(
        reply=result["reply"],
        player_data=result["player_data"],
        player_name=result["player_name"],
        api_calls_today=get_call_count(),
    )


