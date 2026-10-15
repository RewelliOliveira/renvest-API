import secrets
from typing import Optional
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.config import ADMIN_TOKEN, RATE_LIMIT_AUTH_PER_MINUTE, RATE_LIMIT_CHAT_PER_MINUTE
from src.core.rate_limit import SlidingWindowRateLimiter, enforce, ip_rate_limit
from src.core.security import decode_access_token
from src.repositories.user_repository import UserRepository
from src.schemas.auth import UserResponse

security = HTTPBearer(auto_error=True)

auth_limiter = SlidingWindowRateLimiter(RATE_LIMIT_AUTH_PER_MINUTE)
chat_limiter = SlidingWindowRateLimiter(RATE_LIMIT_CHAT_PER_MINUTE)

auth_rate_limit = ip_rate_limit(auth_limiter, "auth")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    """
    Dependência FastAPI que extrai e valida o token Bearer JWT.
    Retorna o perfil do usuário logado ou levanta 401 Unauthorized.
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload["sub"]
    user = UserRepository.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário associado ao token não foi encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserResponse.from_record(user)

def chat_rate_limit(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Garante usuário autenticado e aplica o limite de mensagens por usuário no chat."""
    enforce(chat_limiter, f"chat:{current_user.id}")
    return current_user

def require_admin(x_admin_token: Optional[str] = Header(default=None)) -> None:
    """Protege rotas administrativas com o token estático ADMIN_TOKEN (comparação em tempo constante)."""
    if not ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rotas administrativas desativadas: ADMIN_TOKEN não configurado.",
        )
    if not x_admin_token or not secrets.compare_digest(x_admin_token, ADMIN_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso administrativo negado.",
        )
