from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.core.security import decode_access_token
from src.repositories.user_repository import UserRepository
from src.schemas.auth import UserResponse

security = HTTPBearer(auto_error=True)

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

    return UserResponse(
        id=str(user["id"]),
        email=user["email"],
        name=user["name"],
        picture=user.get("picture"),
        auth_provider=user.get("auth_provider", "local"),
        created_at=str(user.get("created_at")) if user.get("created_at") else None,
    )
