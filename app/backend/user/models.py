import sqlalchemy
from pydantic import EmailStr, SecretStr

from ..base.errors import EntityDoesNotExist
from ..base.models import BaseOps
from ..core.db import metadata
from .schema import UserInDB

user = sqlalchemy.Table(
    "user",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.String(128), unique=True, index=True, nullable=False),
    sqlalchemy.Column("salt", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("hashed_password", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("is_active", sqlalchemy.Boolean, default=True),
    sqlalchemy.Column("is_superuser", sqlalchemy.Boolean, default=False),
)


class UserOps(BaseOps):
    table = user

    async def get_user_by_email(self, email: EmailStr) -> UserInDB:
        query = self.table.select().where(self.table.c.email == email)
        user = await self._log_and_fetch_row(query)
        if user:
            return UserInDB.from_orm(user)
        raise EntityDoesNotExist(f"User with email:{email} not found!")

    async def create_user(self, email: EmailStr, password: SecretStr):
        user = UserInDB(email=email)
        user.change_password(password)
        await self.insert(user.dict(exclude={"id_"}))
        return await self.get_user_by_email(email)
