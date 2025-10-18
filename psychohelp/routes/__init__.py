from fastapi import APIRouter

from .controllers import appointments, images, reviews, roles, therapists, users

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(appointments.router)
api_router.include_router(reviews.router)
api_router.include_router(roles.router)
api_router.include_router(therapists.router)
api_router.include_router(images.router)
