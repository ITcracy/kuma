from fastapi import APIRouter

from .user.routes import router as user_router
from .pandaui.socket import router as pandui_socket

router = APIRouter()
router.include_router(user_router, prefix="/user", tags=["user"])
router.include_router(pandui_socket, prefix="/pandaui", tags=["pandas"])
