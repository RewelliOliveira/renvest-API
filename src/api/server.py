from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import CORS_ORIGINS
from src.api.router import api_router

def create_application() -> FastAPI:
    application = FastAPI(
        title="Renvest - RAG Finance Agent API",
        description="API educacional financeira com RAG e autenticação segura para o Renvest",
        version="1.0.0"
    )

    origins = CORS_ORIGINS if CORS_ORIGINS else ["*"]

    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router)
    return application

app = create_application()
