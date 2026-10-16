from datetime import timedelta

import jwt
import pytest

from src import config
from src.core.rate_limit import SlidingWindowRateLimiter
from src.core.security import create_access_token, decode_access_token, hash_password, verify_password

def test_password_hash_roundtrip():
    hashed = hash_password("SenhaForte@2026")
    assert verify_password("SenhaForte@2026", hashed)
    assert not verify_password("senhaErrada", hashed)

def test_verify_password_without_hash_returns_false():
    assert not verify_password("qualquer", None)

def test_hash_password_rejects_short_password():
    with pytest.raises(ValueError):
        hash_password("123")

def test_jwt_roundtrip_and_expiration():
    token = create_access_token({"sub": "user-1"})
    assert decode_access_token(token)["sub"] == "user-1"

    expired = create_access_token({"sub": "user-1"}, expires_delta=timedelta(seconds=-1))
    assert decode_access_token(expired) is None

def test_jwt_signed_with_other_secret_is_rejected():
    forged = jwt.encode({"sub": "user-1"}, "outro-segredo-qualquer-com-32-caracteres", algorithm="HS256")
    assert decode_access_token(forged) is None

def test_validate_settings_rejects_weak_jwt_secret(monkeypatch):
    monkeypatch.setattr(config, "JWT_SECRET", "curto")
    with pytest.raises(RuntimeError):
        config.validate_settings()

def test_rate_limiter_blocks_after_limit():
    limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=60)
    assert limiter.hit("ip")
    assert limiter.hit("ip")
    assert not limiter.hit("ip")
    assert limiter.hit("outro-ip")

def test_rate_limiter_releases_after_window():
    limiter = SlidingWindowRateLimiter(max_requests=1, window_seconds=0)
    assert limiter.hit("ip")
    assert limiter.hit("ip")

def test_parse_cors_origins_ignores_trailing_slashes_and_blanks():
    raw = " https://renvest-eight.vercel.app/ ,http://localhost:5173,, / "
    assert config.parse_cors_origins(raw) == ["https://renvest-eight.vercel.app", "http://localhost:5173"]
