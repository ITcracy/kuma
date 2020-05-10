from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware

from app.backend.base.errors import http422_error_handler, http_error_handler
from app.backend.core.config import app_config

from .api import router as api_router
from .core.events import close_db_connection, connect_to_db


def get_application() -> FastAPI:
    application = FastAPI(
        title=app_config.PROJECT_NAME, debug=app_config.DEBUG, version=app_config.VERSION,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=app_config.ALLOWED_HOSTS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.on_event("startup")
    async def startup_event():
        await connect_to_db()

    @application.on_event("shutdown")
    async def shutdown_event():
        await close_db_connection()

    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(RequestValidationError, http422_error_handler)

    application.include_router(api_router, prefix=app_config.API_PREFIX)

    return application


app = get_application()
