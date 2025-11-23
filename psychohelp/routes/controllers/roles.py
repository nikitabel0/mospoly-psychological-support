from uuid import UUID

from fastapi import APIRouter, HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

from psychohelp.config.logging import get_logger
from psychohelp.repositories.rbac.exceptions import (
    RoleNotFoundException,
    UserNotFoundException,
)
from psychohelp.repositories.rbac.rbac import (
    assign_role_to_user,
    remove_role_from_user,
)
from psychohelp.schemas.roles import RoleAssignRequest, RoleRemoveRequest

logger = get_logger(__name__)
router = APIRouter(prefix="/roles", tags=["roles"])


@router.post("/{user_id}/assign")
async def assign_role(user_id: UUID, request: RoleAssignRequest) -> dict[str, str]:
    """Назначить роль пользователю"""
    try:
        assigned = await assign_role_to_user(user_id, request.role_code)
        if not assigned:
            logger.info(f"Role '{request.role_code.value}' already assigned to user {user_id}")
            return {"message": f"Роль '{request.role_code.value}' уже назначена пользователю"}
        logger.info(f"Role '{request.role_code.value}' successfully assigned to user {user_id}")
        return {"message": f"Роль '{request.role_code.value}' успешно назначена"}

    except (UserNotFoundException, RoleNotFoundException) as e:
        logger.warning(f"Failed to assign role: {str(e)}")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(e)) from e

    except Exception as e:
        logger.exception(
            f"Unexpected error assigning role '{request.role_code.value}' to user {user_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Не удалось назначить роль"
        ) from e


@router.post("/{user_id}/remove")
async def remove_role(user_id: UUID, request: RoleRemoveRequest) -> dict[str, str]:
    """Убрать роль у пользователя"""
    try:
        removed = await remove_role_from_user(user_id, request.role_code)
        if not removed:
            logger.info(f"Role '{request.role_code.value}' was not assigned to user {user_id}")
            return {"message": f"Роль '{request.role_code.value}' не была назначена пользователю"}
        logger.info(f"Role '{request.role_code.value}' successfully removed from user {user_id}")
        return {"message": f"Роль '{request.role_code.value}' успешно удалена"}

    except UserNotFoundException as e:
        logger.warning(f"Failed to remove role: {str(e)}")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(e)) from e

    except Exception as e:
        logger.exception(
            f"Unexpected error removing role '{request.role_code.value}' from user {user_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Не удалось удалить роль"
        ) from e
