from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Dict
import bcrypt
import jwt
from src.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES

# Hash falso pré-gerado para proteger contra ataques de timing quando o usuário não é encontrado
_DUMMY_HASH = bcrypt.hashpw(b"timing_attack_protection_dummy_password", bcrypt.gensalt(12)).decode("utf-8")

def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        raise ValueError("A senha não pode ultrapassar 72 bytes.")
    if len(password.strip()) < 6:
        raise ValueError("A senha deve ter no mínimo 6 caracteres.")
    
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: Optional[str]) -> bool:
    """
    Verifica se a senha fornecida confere com o hash criptografado.
    Executa verificação dummy caso o hash seja nulo para prevenir enumeração por tempo.
    """
    if not hashed_password:
        dummy_verify_password()
        return False
        
    plain_bytes = plain_password.encode("utf-8")
    if len(plain_bytes) > 72:
        return False
        
    try:
        return bcrypt.checkpw(plain_bytes, hashed_password.encode("utf-8"))
    except Exception:
        return False

def dummy_verify_password() -> None:
    try:
        bcrypt.checkpw(b"invalid_password_timing_check", _DUMMY_HASH.encode("utf-8"))
    except Exception:
        pass

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Gera um token JWT assinado com payload contendo os dados do usuário, emissão e expiração.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=JWT_EXPIRE_MINUTES)
        
    to_encode.update({
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp())
    })
    
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except (jwt.PyJWTError, Exception):
        return None
