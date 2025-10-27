from fastapi import HTTPException, APIRouter

from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from psychohelp.config.logging import get_logger
from psychohelp.services.rbac import get_user_roles
from psychohelp.repositories.rbac import (
    assign_role_to_user,
    remove_role_from_user,
    UserNotFoundException,
    RoleNotFoundException,
    UUID,
)
from psychohelp.schemas.roles import RoleResponse, RoleAssignRequest, RoleRemoveRequest

logger = get_logger(__name__)
router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/{user_id}", response_model=list[RoleResponse])
async def get_roles(user_id: UUID):
    """Получить все роли пользователя"""
    roles = await get_user_roles(user_id)
    return [RoleResponse(code=r.code.name, name=r.name, description=r.description) for r in roles]


@router.post("/{user_id}/assign")
async def assign_role(user_id: UUID, request: RoleAssignRequest):
    """Назначить роль пользователю"""
    try:
        assigned = await assign_role_to_user(user_id, request.role_code)
        if not assigned:
            logger.info(f"Role '{request.role_code}' already assigned to user {user_id}")
            return {"message": f"Роль '{request.role_code}' уже назначена пользователю"}
        logger.info(f"Role '{request.role_code}' successfully assigned to user {user_id}")
        return {"message": f"Роль '{request.role_code}' успешно назначена"}
    
    except (UserNotFoundException, RoleNotFoundException) as e:
        logger.warning(f"Failed to assign role: {str(e)}")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(e))
    
    except Exception as e:
        logger.exception(f"Unexpected error assigning role '{request.role_code}' to user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Не удалось назначить роль"
        )


@router.post("/{user_id}/remove")
async def remove_role(user_id: UUID, request: RoleRemoveRequest):
    """Убрать роль у пользователя"""
    try:
        removed = await remove_role_from_user(user_id, request.role_code)
        if not removed:
            logger.info(f"Role '{request.role_code}' was not assigned to user {user_id}")
            return {"message": f"Роль '{request.role_code}' не была назначена пользователю"}
        logger.info(f"Role '{request.role_code}' successfully removed from user {user_id}")
        return {"message": f"Роль '{request.role_code}' успешно удалена"}
    
    except UserNotFoundException as e:
        logger.warning(f"Failed to remove role: {str(e)}")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(e))
    
    except Exception as e:
        logger.exception(f"Unexpected error removing role '{request.role_code}' from user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Не удалось удалить роль"
        )


