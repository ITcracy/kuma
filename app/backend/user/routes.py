from fastapi import Body, Depends, HTTPException, status

from ..base.errors import EntityDoesNotExist
from ..base.routes import CRUDRouter
from ..core.config import app_config
from ..core.resources import EMAIL_TAKEN, INCORRECT_LOGIN_INPUT
from ..services import jwt
from .dependencies import check_email_is_taken, get_current_user_authorizer
from .models import UserOps
from .schema import UserWithID, UserInRequest, UserWithToken

router = CRUDRouter()
router.init_crud(
    ops=UserOps,
    schema_in={"create": UserInRequest},
    schema_out={"read": UserWithID},
    dependencies={
        "read": [Depends(get_current_user_authorizer())],
        "remove": [Depends(get_current_user_authorizer())],
    },
)


@router.post("/login", response_model=UserWithToken, name="auth:login")
async def login(
    user_login: UserInRequest = Body(..., embed=True, alias="user"), user_ops: UserOps = Depends(),
):
    wrong_login_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail=INCORRECT_LOGIN_INPUT,
    )

    try:
        user = await user_ops.get_user_by_email(email=user_login.email)
    except EntityDoesNotExist as existence_error:
        raise wrong_login_error from existence_error

    if not user.check_password(user_login.password):
        raise wrong_login_error

    token = jwt.create_access_token_for_user(user, str(app_config.SECRET_KEY))
    return UserWithToken(id=user.id_, email=user.email, token=token)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserWithToken,
    name="auth:register",
)
async def register(
    user_create: UserInRequest = Body(..., embed=True, alias="user"),
    users_repo: UserOps = Depends(),
) -> UserWithToken:
    if await check_email_is_taken(users_repo, user_create.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=EMAIL_TAKEN,
        )

    user = await users_repo.create_user(**user_create.dict())

    token = jwt.create_access_token_for_user(user, str(app_config.SECRET_KEY))
    return UserWithToken(id=user.id_, email=user.email, token=token)
