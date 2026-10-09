from fastapi import Request, HTTPException, Depends
from starlette.status import HTTP_401_UNAUTHORIZED
from psychohelp.services.users.users import get_user_by_token
from psychohelp.models.users import User
from fastapi.security import APIKeyCookie
import jwt

cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)

async def get_current_user(token: str = Depends(cookie_scheme)) -> User:
    """Dependency для получения текущего пользователя из токена"""
    if not token:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, 
            detail="Пользователь не авторизован"
        )

    try:
        user = await get_user_by_token(token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Недействительный или просроченный токен"
        )

    if user is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, 
            detail="Пользователь не авторизован"
        )
        
    return user
    



async def get_optional_user(request: Request) -> User | None:
    """Dependency для опционального получения пользователя (если токен есть)"""
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    return await get_user_by_token(token)