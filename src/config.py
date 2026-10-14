import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
VECTOR_DB_DIR = DATA_DIR / "vector_db"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Modelos e RAG
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()

# Segurança e JWT
JWT_SECRET = os.getenv("JWT_SECRET", "").strip()
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "10080"))  # 7 dias
JWT_MIN_SECRET_LENGTH = 32

# Token exigido no header X-Admin-Token para rotas administrativas (vazio = rotas desativadas)
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "").strip()

# Google OAuth (obrigatório para validar a audiência dos tokens do Google)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()

# Rate limiting (requisições por janela de 60 segundos)
RATE_LIMIT_AUTH_PER_MINUTE = int(os.getenv("RATE_LIMIT_AUTH_PER_MINUTE", "10"))
RATE_LIMIT_CHAT_PER_MINUTE = int(os.getenv("RATE_LIMIT_CHAT_PER_MINUTE", "15"))

# CORS
cors_raw = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173")
CORS_ORIGINS = [origin.strip() for origin in cors_raw.split(",") if origin.strip()]


def validate_settings() -> None:
    """Falha cedo na inicialização da API caso configurações críticas de segurança estejam ausentes."""
    if len(JWT_SECRET) < JWT_MIN_SECRET_LENGTH:
        raise RuntimeError(
            f"JWT_SECRET ausente ou fraco: defina no .env um segredo aleatório com no mínimo "
            f"{JWT_MIN_SECRET_LENGTH} caracteres (ex: python -c \"import secrets; print(secrets.token_urlsafe(48))\")."
        )
    if not CORS_ORIGINS:
        raise RuntimeError("CORS_ORIGINS não pode ser vazio.")
