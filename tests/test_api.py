from src.api.routes import admin
from src.schemas.chat import ChatResponse
from src.services import auth_service
from src.services.chat_service import ChatService

def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok", "agent": "Rev"}

def test_ingest_requires_admin_token(client, monkeypatch):
    calls = []
    monkeypatch.setattr(admin, "run_ingestion", lambda: calls.append(True))

    assert client.post("/api/ingest").status_code == 403
    assert client.post("/api/ingest", headers={"X-Admin-Token": "errado"}).status_code == 403
    assert calls == []

    response = client.post("/api/ingest", headers={"X-Admin-Token": "test-admin-token"})
    assert response.status_code == 200
    assert calls == [True]

def test_chat_requires_authentication(client):
    assert client.post("/api/chat", json={"message": "Oi"}).status_code == 401

def test_chat_rejects_invalid_token(client):
    response = client.post("/api/chat", json={"message": "Oi"}, headers={"Authorization": "Bearer invalido"})
    assert response.status_code == 401

def test_chat_authenticated_passes_first_name_and_history(client, auth_headers, monkeypatch):
    received = {}

    def fake_process_message(message, module, history, user_name):
        received.update(message=message, user_name=user_name, history=history)
        return ChatResponse(reply="Olá!", source=None, suggestions=["O que é FGC?"])

    monkeypatch.setattr(ChatService, "process_message", staticmethod(fake_process_message))
    response = client.post(
        "/api/chat",
        json={"message": "O que é CDB?", "history": [{"role": "user", "content": "Oi"}]},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["reply"] == "Olá!"
    assert received["user_name"] == "Antonio"
    assert received["history"][0].content == "Oi"

def test_chat_rate_limit_per_user(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        ChatService,
        "process_message",
        staticmethod(lambda **_: ChatResponse(reply="ok", suggestions=[])),
    )
    codes = [client.post("/api/chat", json={"message": "Oi"}, headers=auth_headers).status_code for _ in range(3)]
    assert codes == [200, 200, 429]

def test_login_rate_limit_per_ip(client, monkeypatch):
    monkeypatch.setattr(auth_service.UserRepository, "get_by_email", classmethod(lambda cls, email: None))
    payload = {"email": "a@b.com", "password": "x"}
    codes = [client.post("/api/auth/login", json=payload).status_code for _ in range(4)]
    assert codes == [401, 401, 401, 429]

def test_suggestions_are_public(client):
    response = client.get("/api/chat/suggestions?module=modulo_1")
    assert response.status_code == 200
    assert len(response.json()["suggestions"]) > 0

def test_unhandled_errors_do_not_leak_details(client, auth_headers, monkeypatch):
    def boom(**_):
        raise RuntimeError("segredo interno")

    monkeypatch.setattr(ChatService, "process_message", staticmethod(boom))
    response = client.post("/api/chat", json={"message": "Oi"}, headers=auth_headers)
    assert response.status_code == 500
    assert "segredo" not in response.text
