from fastapi import HTTPException, APIRouter, Request, Response

from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY, HTTP_403_FORBIDDEN,
)
from pydantic import EmailStr

from psychohelp.config.logging import get_logger
from psychohelp.services.users import users
from psychohelp.services.users import exceptions as users_exceptions

from psychohelp.schemas.users import (
    LoginRequest,
    UserCreateRequest,
    UserResponse,
)
from . import set_token_in_cookie

logger = get_logger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


@router.get("/user", response_model=UserResponse)
async def user_token(request: Request) -> UserResponse:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Пользователь не авторизован"
        )
    
    user = await users.get_user_by_token(token)
    if user is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    return user


@router.get("/user/{id}", response_model=UserResponse)
async def user(id: users.UUID) -> UserResponse:
    user = await users.get_user_by_id(id)
    if user is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    return user


@router.post("/register", response_model=UserResponse)
async def register_users(user_data: UserCreateRequest, response: Response) -> UserResponse:
    try:
        user, token = await users.register_user(**user_data.model_dump())
        set_token_in_cookie(response, token)
        response.status_code = HTTP_201_CREATED
    except ValueError as exc:
        # todo: нельзя так исключение наружу отдавать
        raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    return user


@router.post("/login", response_model=UserResponse)
async def login(data: LoginRequest, response: Response) -> UserResponse:
    try:
        user_with_token = await users.login_user(data.email, data.password)
        user = user_with_token.user
        token = user_with_token.token

        set_token_in_cookie(response, token)
        response.status_code = HTTP_200_OK
        return user
    except (users_exceptions.UserNotFound, users_exceptions.WrongPassword):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Неверные данные"
        )


@router.post("/logout")
async def logout(request: Request, response: Response) -> Response:
    token = request.cookies.get("access_token")
    if token is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Пользователь не авторизован"
        )

    response.status_code = HTTP_200_OK
    response.delete_cookie("access_token")
    return response
