from datetime import datetime, timedelta
from typing import Dict

import jwt
from pydantic import EmailStr, ValidationError

from ..core.config import app_config
from ..user.schema import JWTMeta, User


def create_jwt_token(
    *, jwt_content: Dict[str, str], secret_key: str, expires_delta: timedelta,
) -> str:
    to_encode = jwt_content.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update(JWTMeta(exp=expire, sub=app_config.JWT_SUBJECT).dict())
    return jwt.encode(to_encode, secret_key, algorithm=app_config.ALGORITHM).decode()


def create_access_token_for_user(user: User, secret_key: str) -> str:
    return create_jwt_token(
        jwt_content=user.dict(),
        secret_key=secret_key,
        expires_delta=timedelta(minutes=app_config.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def get_email_from_token(token: str, secret_key: str) -> EmailStr:
    try:
        return User(**jwt.decode(token, secret_key, algorithms=[app_config.ALGORITHM])).email
    except jwt.PyJWTError as decode_error:
        raise ValueError("unable to decode JWT token") from decode_error
    except ValidationError as validation_error:
        raise ValueError("malformed payload in token") from validation_error
