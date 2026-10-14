import logging
from typing import Optional, Dict, Any
import httpx
from fastapi import HTTPException, status
from src.config import GOOGLE_CLIENT_ID
from src.core.database import is_supabase_configured
from src.core.security import hash_password, verify_password, dummy_verify_password, create_access_token
from src.repositories.user_repository import UserRepository
from src.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    GoogleAuthRequest,
    UserResponse,
    AuthResponse,
)

logger = logging.getLogger(__name__)

GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
GOOGLE_TIMEOUT_SECONDS = 8.0

class AuthService:

    @staticmethod
    def _is_verified(value: Any) -> bool:
        return value is True or str(value).lower() == "true"

    @classmethod
    def _verify_google_token(cls, payload: GoogleAuthRequest) -> Optional[Dict[str, Any]]:
        """Retorna as claims do Google apenas se o token for do nosso client e o e-mail estiver verificado."""
        if payload.id_token:
            resp = httpx.get(
                GOOGLE_TOKENINFO_URL,
                params={"id_token": payload.id_token},
                timeout=GOOGLE_TIMEOUT_SECONDS,
            )
            if resp.status_code != 200:
                return None
            claims = resp.json()
            audience = claims.get("aud")
        else:
            token_resp = httpx.get(
                GOOGLE_TOKENINFO_URL,
                params={"access_token": payload.access_token},
                timeout=GOOGLE_TIMEOUT_SECONDS,
            )
            if token_resp.status_code != 200:
                return None
            token_info = token_resp.json()
            audience = token_info.get("azp") or token_info.get("aud")

            profile_resp = httpx.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {payload.access_token}"},
                timeout=GOOGLE_TIMEOUT_SECONDS,
            )
            if profile_resp.status_code != 200:
                return None
            claims = profile_resp.json()
            if claims.get("sub") != token_info.get("sub"):
                return None

        if audience != GOOGLE_CLIENT_ID:
            logger.warning("Token Google rejeitado: audiência não corresponde ao GOOGLE_CLIENT_ID")
            return None
        if not claims.get("sub") or not claims.get("email"):
            return None
        if not cls._is_verified(claims.get("email_verified")):
            return None
        return claims

    @classmethod
    def _check_db_available(cls) -> None:
        if not is_supabase_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Credenciais do supabase não configuradas",
            )

    @classmethod
    def _to_user_response(cls, user_data: Dict[str, Any]) -> UserResponse:
        return UserResponse(
            id=str(user_data["id"]),
            email=user_data["email"],
            name=user_data["name"],
            picture=user_data.get("picture"),
            auth_provider=user_data.get("auth_provider", "local"),
            created_at=str(user_data.get("created_at")) if user_data.get("created_at") else None,
        )

    @classmethod
    def register(cls, payload: UserRegisterRequest) -> AuthResponse:
        cls._check_db_available()

        existing = UserRepository.get_by_email(payload.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este e-mail já está cadastrado no sistema.",
            )

        try:
            pwd_hash = hash_password(payload.password)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        user = UserRepository.create_local_user(
            name=payload.name,
            email=payload.email,
            password_hash=pwd_hash,
        )

        token = create_access_token({"sub": str(user["id"]), "email": user["email"]})
        return AuthResponse(
            user=cls._to_user_response(user),
            access_token=token,
            token_type="bearer",
        )

    @classmethod
    def login(cls, payload: UserLoginRequest) -> AuthResponse:
        cls._check_db_available()

        user = UserRepository.get_by_email(payload.email)
        if not user:
            dummy_verify_password()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="E-mail ou senha incorretos.",
            )

        pwd_hash = user.get("password_hash")
        if not pwd_hash or not verify_password(payload.password, pwd_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="E-mail ou senha incorretos.",
            )

        token = create_access_token({"sub": str(user["id"]), "email": user["email"]})
        return AuthResponse(
            user=cls._to_user_response(user),
            access_token=token,
            token_type="bearer",
        )

    @classmethod
    def authenticate_google(cls, payload: GoogleAuthRequest) -> AuthResponse:
        cls._check_db_available()

        if not GOOGLE_CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Login com Google não está configurado no servidor.",
            )

        if not payload.access_token and not payload.id_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Informe um token do Google válido (access_token ou id_token).",
            )

        try:
            google_user_info = cls._verify_google_token(payload)
        except httpx.HTTPError:
            logger.exception("Falha de comunicação com os servidores do Google")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Não foi possível validar o login com o Google agora. Tente novamente.",
            )

        if not google_user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de autenticação do Google inválido ou expirado.",
            )

        email = google_user_info["email"]
        name = google_user_info.get("name") or email.split("@")[0]
        google_id = google_user_info["sub"]
        picture = google_user_info.get("picture")

        user = UserRepository.upsert_google_user(
            email=email,
            name=name,
            google_id=google_id,
            picture=picture,
        )

        token = create_access_token({"sub": str(user["id"]), "email": user["email"]})
        return AuthResponse(
            user=cls._to_user_response(user),
            access_token=token,
            token_type="bearer",
        )
