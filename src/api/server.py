from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.agents.assistant import chat_rag
from src.database.ingest import run_ingestion

app = FastAPI(
    title="Renvest - RAG Finance Agent API",
    description="API do assistente educacional financeiro para o frontend Renvest",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    module: Optional[str] = "modulo_1"

class SourceResponse(BaseModel):
    document: str
    section: str
    institution: Optional[str] = None
    url: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    source: SourceResponse

@app.get("/api/health")
def health_check():
    return {"status": "ok", "agent": "Rev"}

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest):
    result = chat_rag(message=payload.message, module=payload.module or "modulo_1")
    return result

@app.post("/api/ingest")
def trigger_ingest():
    run_ingestion()
    return {"status": "Ingestão executada com sucesso!"}
