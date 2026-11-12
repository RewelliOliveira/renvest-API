import pytest
from src.core.name_validation import validate_name
from src.services import auth_service

PAYLOAD = {"name": "Maria Silva", "email": "maria@exemplo.com", "password": "senha123"}

@pytest.fixture
def created_users(monkeypatch):
    users = []

    def create_local_user(cls, name, email, password_hash):
        user = {"id": "22222222-2222-2222-2222-222222222222", "name": name, "email": email, "auth_provider": "local"}
        users.append(user)
        return user

    monkeypatch.setattr(auth_service.UserRepository, "get_by_email", classmethod(lambda cls, email: None))
    monkeypatch.setattr(auth_service.UserRepository, "create_local_user", classmethod(create_local_user))
    return users

def register(client, **overrides):
    return client.post("/api/auth/register", json={**PAYLOAD, **overrides})

@pytest.mark.parametrize("name", ["Maria Silva", "José", "João Pedro", "Ana-Clara", "D'Ávila Souza", "Yasmin", "Kauã", "joao123", "Maria 123", "ana.clara", "biel_22"])
def test_accepts_real_names(name):
    assert validate_name(name) is None

@pytest.mark.parametrize("name", ["aksjhdjagdjs", "asdasd", "qwerty", "asdfgh", "kakaka", "bcdf", "a", "123", "j1", "qwerty99", "maria!"])
def test_rejects_gibberish_names(name):
    assert validate_name(name) is not None

def test_register_rejects_gibberish_name(client, created_users):
    assert register(client, name="aksjhdjagdjs").status_code == 400
    assert created_users == []

def test_register_with_valid_name_creates_user(client, created_users):
    response = register(client)
    assert response.status_code == 200
    assert len(created_users) == 1
