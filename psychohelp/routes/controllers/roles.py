from uuid import UUID

from fastapi import HTTPException, APIRouter, Request

from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from psychohelp.config.logging import get_logger
from psychohelp.repositories.rbac.rbac import (
    assign_role_to_user,
    remove_role_from_user,
)
from psychohelp.repositories.rbac.exceptions import (
    UserNotFoundException,
    RoleNotFoundException,
)
from psychohelp.schemas.roles import RoleAssignRequest, RoleRemoveRequest
from psychohelp.services.rbac.permissions import require_permission
from psychohelp.constants.rbac import PermissionCode

logger = get_logger(__name__)
router = APIRouter(prefix="/roles", tags=["roles"])


@router.post("/{user_id}/assign")
@require_permission(PermissionCode.ROLES_ASSIGN)
async def assign_role(request: Request, user_id: UUID, data: RoleAssignRequest) -> dict[str, str]:
    """Назначить роль пользователю"""
    try:
        assigned = await assign_role_to_user(user_id, data.role_code)
        if not assigned:
            logger.info(f"Role '{data.role_code.value}' already assigned to user {user_id}")
            return {"message": f"Роль '{data.role_code.value}' уже назначена пользователю"}
        logger.info(f"Role '{data.role_code.value}' successfully assigned to user {user_id}")
        return {"message": f"Роль '{data.role_code.value}' успешно назначена"}
    
    except (UserNotFoundException, RoleNotFoundException) as e:
        logger.warning(f"Failed to assign role: {str(e)}")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(e))
    
    except Exception as e:
        logger.exception(f"Unexpected error assigning role '{data.role_code.value}' to user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Не удалось назначить роль"
        )


@router.post("/{user_id}/remove")
@require_permission(PermissionCode.ROLES_REMOVE)
async def remove_role(request: Request, user_id: UUID, data: RoleRemoveRequest) -> dict[str, str]:
    """Убрать роль у пользователя"""
    try:
        removed = await remove_role_from_user(user_id, data.role_code)
        if not removed:
            logger.info(f"Role '{data.role_code.value}' was not assigned to user {user_id}")
            return {"message": f"Роль '{data.role_code.value}' не была назначена пользователю"}
        logger.info(f"Role '{data.role_code.value}' successfully removed from user {user_id}")
        return {"message": f"Роль '{data.role_code.value}' успешно удалена"}
    
    except UserNotFoundException as e:
        logger.warning(f"Failed to remove role: {str(e)}")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(e))
    
    except Exception as e:
        logger.exception(f"Unexpected error removing role '{data.role_code.value}' from user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Не удалось удалить роль"
        )


