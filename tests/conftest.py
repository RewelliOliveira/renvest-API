import os

# Configuração isolada para os testes; definida antes de importar src.* (load_dotenv não sobrescreve)
os.environ["JWT_SECRET"] = "test-secret-with-at-least-thirty-two-characters"
os.environ["ADMIN_TOKEN"] = "test-admin-token"
os.environ["GOOGLE_CLIENT_ID"] = "test-client-id.apps.googleusercontent.com"
os.environ["SUPABASE_URL"] = "https://example.supabase.co"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "test-service-role-key"
os.environ["OPENAI_API_KEY"] = "sk-test"
os.environ["RATE_LIMIT_AUTH_PER_MINUTE"] = "3"
os.environ["RATE_LIMIT_CHAT_PER_MINUTE"] = "2"

import pytest
from fastapi.testclient import TestClient

from src.api import dependencies
from src.api.server import app
from src.core.security import create_access_token

TEST_USER = {
    "id": "11111111-1111-1111-1111-111111111111",
    "email": "investidor@renvest.com.br",
    "name": "Antonio Investidor",
    "picture": None,
    "auth_provider": "local",
    "created_at": "2026-10-13T00:00:00+00:00",
}

@pytest.fixture(autouse=True)
def reset_rate_limiters():
    dependencies.auth_limiter.reset()
    dependencies.chat_limiter.reset()

@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)

@pytest.fixture
def auth_headers(monkeypatch):
    monkeypatch.setattr(
        dependencies.UserRepository,
        "get_by_id",
        classmethod(lambda cls, user_id: TEST_USER if user_id == TEST_USER["id"] else None),
    )
    token = create_access_token({"sub": TEST_USER["id"], "email": TEST_USER["email"]})
    return {"Authorization": f"Bearer {token}"}
