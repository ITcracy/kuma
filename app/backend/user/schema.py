from datetime import datetime

from pydantic import BaseModel, EmailStr, SecretStr

from ..base.schema import IDModelMixin, RWModel
from ..services import security


class User(RWModel):
    email: EmailStr


class UserWithID(User, IDModelMixin):
    pass


class UserInRequest(User):
    password: SecretStr


class UserInDB(IDModelMixin, User):
    salt: str = ""
    hashed_password: str = ""

    def check_password(self, password: SecretStr) -> bool:
        return security.verify_password(
            plain_password=f"{self.salt}{password.get_secret_value()}",
            hashed_password=self.hashed_password,
        )

    def change_password(self, password: SecretStr) -> None:
        self.salt = security.generate_salt()
        self.hashed_password = security.get_password_hash(
            f"{self.salt}{password.get_secret_value()}"
        )


class UserWithToken(UserWithID):
    token: str


class JWTMeta(BaseModel):
    exp: datetime
    sub: str
