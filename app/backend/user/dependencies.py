from typing import Callable, Optional

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import EmailStr
from starlette import requests, status
from starlette.exceptions import HTTPException as StarletteHTTPException

from ..base.errors import EntityDoesNotExist
from ..core import resources
from ..core.config import app_config
from ..services import jwt
from .models import UserOps
from .schema import User

HEADER_KEY = "Authorization"


class RWAPIKeyHeader(APIKeyHeader):
    async def __call__(self, request: requests.Request,) -> Optional[str]:  # noqa: WPS610
        try:
            return await super().__call__(request)
        except StarletteHTTPException as original_auth_exc:
            raise HTTPException(
                status_code=original_auth_exc.status_code, detail=resources.AUTHENTICATION_REQUIRED,
            )


async def check_email_is_taken(repo: UserOps, email: EmailStr) -> bool:
    try:
        await repo.get_user_by_email(email=email)
    except EntityDoesNotExist:
        return False

    return True


def get_current_user_authorizer(*, required: bool = True) -> Callable:  # type: ignore
    return _get_current_user if required else _get_current_user_optional


def _get_authorization_header_retriever(*, required: bool = True,) -> Callable:  # type: ignore
    return _get_authorization_header if required else _get_authorization_header_optional


def _get_authorization_header(api_key: str = Security(RWAPIKeyHeader(name=HEADER_KEY)),) -> str:
    try:
        token_prefix, token = api_key.split(" ")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=resources.WRONG_TOKEN_PREFIX,
        )

    if token_prefix != app_config.JWT_TOKEN_PREFIX:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=resources.WRONG_TOKEN_PREFIX,
        )

    return token


def _get_authorization_header_optional(
    authorization: Optional[str] = Security(RWAPIKeyHeader(name=HEADER_KEY, auto_error=False),),
) -> str:
    if authorization:
        return _get_authorization_header(authorization)

    return ""


async def _get_current_user(
    user_ops: UserOps = Depends(), token: str = Depends(_get_authorization_header_retriever()),
) -> User:
    try:
        email = jwt.get_email_from_token(token, str(app_config.SECRET_KEY))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=resources.MALFORMED_PAYLOAD,
        )

    try:
        return await user_ops.get_user_by_email(email)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=resources.MALFORMED_PAYLOAD,
        )


async def _get_current_user_optional(
    user_ops: UserOps = Depends(),
    token: str = Depends(_get_authorization_header_retriever(required=False)),
) -> Optional[User]:
    if token:
        return await _get_current_user(user_ops, token)

    return None
