from fastapi import APIRouter, Depends
from src.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    GoogleAuthRequest,
    UserResponse,
    AuthResponse,
)
from src.services.auth_service import AuthService
from src.api.dependencies import get_current_user, auth_rate_limit

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=AuthResponse, dependencies=[Depends(auth_rate_limit)])
def register(payload: UserRegisterRequest):
    return AuthService.register(payload)

@router.post("/login", response_model=AuthResponse, dependencies=[Depends(auth_rate_limit)])
def login(payload: UserLoginRequest):
    return AuthService.login(payload)

@router.post("/google", response_model=AuthResponse, dependencies=[Depends(auth_rate_limit)])
def authenticate_google(payload: GoogleAuthRequest):
    return AuthService.authenticate_google(payload)

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: UserResponse = Depends(get_current_user)):
    return current_user
