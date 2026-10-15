from src.schemas.auth import GoogleAuthRequest
from src.services import auth_service
from src.services.auth_service import AuthService

CLIENT_ID = "test-client-id.apps.googleusercontent.com"
PROFILE = {"sub": "google-1", "email": "user@gmail.com", "email_verified": True, "name": "User"}

class FakeResponse:
    def __init__(self, status_code, data):
        self.status_code = status_code
        self._data = data

    def json(self):
        return self._data

def mock_google(monkeypatch, token_info, profile):
    def fake_get(url, **kwargs):
        if url == auth_service.GOOGLE_TOKENINFO_URL:
            return FakeResponse(200, token_info)
        return FakeResponse(200, profile)

    monkeypatch.setattr(auth_service.httpx, "get", fake_get)

def verify():
    return AuthService._verify_google_token(GoogleAuthRequest(access_token="token"))

def test_accepts_token_from_our_client(monkeypatch):
    mock_google(monkeypatch, {"azp": CLIENT_ID, "sub": "google-1"}, PROFILE)
    assert verify()["email"] == "user@gmail.com"

def test_rejects_token_issued_to_another_client(monkeypatch):
    mock_google(monkeypatch, {"azp": "outro-app", "sub": "google-1"}, PROFILE)
    assert verify() is None

def test_rejects_unverified_email(monkeypatch):
    mock_google(monkeypatch, {"azp": CLIENT_ID, "sub": "google-1"}, {**PROFILE, "email_verified": False})
    assert verify() is None

def test_rejects_profile_from_different_subject(monkeypatch):
    mock_google(monkeypatch, {"azp": CLIENT_ID, "sub": "google-2"}, PROFILE)
    assert verify() is None

def test_google_endpoint_returns_401_for_invalid_token(client, monkeypatch):
    mock_google(monkeypatch, {"azp": "outro-app", "sub": "google-1"}, PROFILE)
    response = client.post("/api/auth/google", json={"access_token": "token"})
    assert response.status_code == 401
