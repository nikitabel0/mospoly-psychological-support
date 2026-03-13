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

from starlette.status import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT
from uuid import UUID
from psychohelp.schemas.users import UserUpdateRequest, PasswordChangeRequest
from psychohelp.services.users.users import update_profile, change_password
from psychohelp.services.users.exceptions import PermissionDenied, UserNotFound
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
            status_code=HTTP_401_UNAUTHORIZED, detail="Неверные данные"
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
@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    request: Request,
    data: UserUpdateRequest
) -> UserResponse:
    """Обновление своего профиля (требуется авторизация)"""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Пользователь не авторизован"
        )

    user_id = get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен"
        )

    try:
        updated_user = await update_profile(
            current_user_id=user_id,
            target_user_id=user_id,
            data=data,
            is_admin=False
        )
    except UserNotFound:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    except PermissionDenied as e:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except HTTPException as e:
        raise e

    return UserResponse.from_orm(updated_user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_by_id(
    request: Request,
    user_id: UUID,
    data: UserUpdateRequest
) -> UserResponse:
    """Обновление профиля любого пользователя (только для администраторов)"""
    token = request.cookies.get("access_token")
    current_user_id = get_user_id_from_token(token) if token else None

    try:
        updated_user = await update_profile(
            current_user_id=current_user_id,
            target_user_id=user_id,
            data=data,
            is_admin=True  # предполагаем, что админ
        )
    except UserNotFound:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    except PermissionDenied as e:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except HTTPException as e:
        raise e

    return UserResponse.from_orm(updated_user)


@router.post("/me/password", status_code=HTTP_200_OK)
async def change_my_password(
    request: Request,
    data: PasswordChangeRequest
) -> dict:
    """Смена пароля текущего пользователя"""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Пользователь не авторизован"
        )

    user_id = get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен"
        )

    try:
        await change_password(user_id, data.old_password, data.new_password)
    except UserNotFound:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return {"message": "Пароль успешно изменён"}