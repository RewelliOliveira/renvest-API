from typing import Optional, Dict, Any
import httpx
from fastapi import HTTPException, status
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

class AuthService:

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

        if not payload.access_token and not payload.id_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Informe um token do Google válido (access_token ou id_token).",
            )

        google_user_info: Optional[Dict[str, Any]] = None

        try:
            if payload.access_token:
                # Valida access_token com a API do Google UserInfo
                resp = httpx.get(
                    "https://www.googleapis.com/oauth2/v3/userinfo",
                    headers={"Authorization": f"Bearer {payload.access_token}"},
                    timeout=8.0,
                )
                if resp.status_code == 200:
                    google_user_info = resp.json()
            elif payload.id_token:
                # Valida id_token com tokeninfo do Google
                resp = httpx.get(
                    f"https://oauth2.googleapis.com/tokeninfo?id_token={payload.id_token}",
                    timeout=8.0,
                )
                if resp.status_code == 200:
                    google_user_info = resp.json()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Erro ao comunicar com os servidores do Google: {str(e)}",
            )

        if not google_user_info or "sub" not in google_user_info or "email" not in google_user_info:
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

    @classmethod
    def get_me(cls, user_id: str) -> UserResponse:
        cls._check_db_available()
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado.",
            )
        return cls._to_user_response(user)
