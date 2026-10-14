from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import CORS_ORIGINS, validate_settings
from src.api.router import api_router

def create_application() -> FastAPI:
    validate_settings()

    application = FastAPI(
        title="Renvest - RAG Finance Agent API",
        description="API educacional financeira com RAG e autenticação segura para o Renvest",
        version="1.0.0"
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Admin-Token"],
    )

    application.include_router(api_router)
    return application

app = create_application()
