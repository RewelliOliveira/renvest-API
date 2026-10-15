import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.config import CORS_ORIGINS, validate_settings
from src.core.logging_config import setup_logging
from src.api.router import api_router

logger = logging.getLogger(__name__)

async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Erro não tratado em %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno no servidor. Tente novamente em instantes."},
    )

def create_application() -> FastAPI:
    setup_logging()
    validate_settings()

    application = FastAPI(
        title="Renvest - RAG Finance Agent API",
        description="API educacional financeira com RAG e autenticação segura para o Renvest",
        version="1.0.0"
    )

    # Autenticação via header Bearer (sem cookies), por isso allow_credentials=False
    application.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Admin-Token"],
    )

    application.add_exception_handler(Exception, unhandled_exception_handler)
    application.include_router(api_router)
    return application

app = create_application()
