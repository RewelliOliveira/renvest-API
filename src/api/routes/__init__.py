from src.api.routes.health import router as health_router
from src.api.routes.chat import router as chat_router
from src.api.routes.modules import router as modules_router
from src.api.routes.admin import router as admin_router
from src.api.routes.auth import router as auth_router
from src.api.routes.trail import router as trail_router

__all__ = [
    "health_router",
    "chat_router",
    "modules_router",
    "admin_router",
    "auth_router",
    "trail_router",
]
