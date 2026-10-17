from fastapi import APIRouter
from src.api.routes.health import router as health_router
from src.api.routes.chat import router as chat_router
from src.api.routes.modules import router as modules_router
from src.api.routes.admin import router as admin_router
from src.api.routes.auth import router as auth_router
from src.api.routes.trail import router as trail_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(modules_router)
api_router.include_router(trail_router)
api_router.include_router(admin_router)
