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

from . import set_token_in_cookie, set_refresh_token_in_cookie
from psychohelp.services.rbac.permissions import user_has_permission
from psychohelp.constants.rbac import PermissionCode
from psychohelp.repositories import get_user_id_from_token

logger = get_logger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


@router.get("/user", response_model=UserResponse)
async def user_token(request: Request) -> UserResponse:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Пользователь не авторизован"
        )
    
    try:
        user = await users.get_user_by_token(token)
    except Exception:
        # Невалидный токен (ошибка декодирования)
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Невалидный токен"
        ) from None
    
    if user is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    return user


@router.get("/user/{id}", response_model=UserResponse)
async def user(request: Request, id: users.UUID) -> UserResponse:
    # Проверяем авторизацию
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Пользователь не авторизован"
        )
    
    # Получаем ID текущего пользователя
    try:
        current_user_id = get_user_id_from_token(token)
    except Exception:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Невалидный токен"
        )
    
    # Проверяем, может ли пользователь просматривать чужие профили
    if current_user_id != id:
        has_permission = await user_has_permission(current_user_id, PermissionCode.USERS_VIEW_ANY)
        if not has_permission:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, 
                detail="Недостаточно прав для просмотра профиля другого пользователя"
            )
    
    user = await users.get_user_by_id(id)
    if user is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    return user


@router.post("/register", response_model=UserResponse)
async def register_users(user_data: UserCreateRequest, response: Response) -> UserResponse:
    try:
        user, token, refresh_token = await users.register_user(**user_data.model_dump())
        set_token_in_cookie(response, token)
        set_refresh_token_in_cookie(response, refresh_token)
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
        refresh_token = user_with_token.refresh_token

        set_token_in_cookie(response, token)
        set_refresh_token_in_cookie(response, refresh_token)
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
    response.delete_cookie("refresh_token")
    return response

@router.post("/refresh", response_model=UserResponse)
async def refresh_token(request: Request, response: Response) -> UserResponse:
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Пользователь не авторизован"
        )
    try:
        new_access_token = users.refresh_access_token(refresh_token)
        user = await users.get_user_by_token(new_access_token)
        if user is None:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Пользователь не найден"
            )
        set_token_in_cookie(response, new_access_token)
        response.status_code = HTTP_200_OK
        return user
    except users_exceptions.InvalidToken:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Недействительный токен обновления"
        )