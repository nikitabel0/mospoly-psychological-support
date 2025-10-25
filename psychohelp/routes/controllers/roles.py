from fastapi import HTTPException, APIRouter, Response

from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from psychohelp.services.roles import (
    get_roles_by_user_id,
    add_roles_by_user_id,
    delete_roles_by_user_id,
    UserRole,
    UUID,
)

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/{user_id}", response_model=list[UserRole])
async def get_roles(user_id: UUID):
    roles = [r.role for r in await get_roles_by_user_id(user_id)]
    return roles


@router.put("/{user_id}")
async def add_roles(user_id: UUID, roles: list[UserRole]):
    if not roles:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Список ролей пуст"
        )
    try:
        await add_roles_by_user_id(user_id, roles)
    except:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось добавить роли",
        )
    return Response(None, HTTP_200_OK)


@router.delete("/{user_id}")
async def delete_roles(user_id: UUID, roles: list[UserRole]):
    if not roles:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Список ролей пуст"
        )
    try:
        await delete_roles_by_user_id(user_id, roles)
    except:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Не удалось удалить роли"
        )
    return Response(None, HTTP_200_OK)
