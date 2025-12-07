from fastapi import HTTPException, APIRouter, Request

from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from psychohelp.config.logging import get_logger
from psychohelp.repositories import get_user_id_from_token
from psychohelp.services.reviews import get_review_by_id, UUID
from psychohelp.services.appointments.appointments import get_appointment_by_id
from psychohelp.schemas.reviews import ReviewsBase


logger = get_logger(__name__)
router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/{review_id}", response_model=ReviewsBase)
async def get_review(request: Request, review_id: UUID):
    """Получить отзыв по ID записи (review_id = appointment_id)"""
    review = await get_review_by_id(review_id)
    if review is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Review not found")
    
    # Проверяем, что appointment принадлежит текущему пользователю
    appointment = await get_appointment_by_id(review_id)
    if appointment is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Appointment not found")
    
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Пользователь не авторизован")
    
    user_id = get_user_id_from_token(token)
    if appointment.patient_id != user_id and appointment.psychologist_id != user_id:
        logger.warning(f"User {user_id} attempted to access review for appointment {review_id} that doesn't belong to them")
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Доступ запрещен: отзыв не принадлежит вам")
    
    return review
