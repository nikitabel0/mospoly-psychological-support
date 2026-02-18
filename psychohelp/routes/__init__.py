from fastapi import APIRouter
from .controllers import users
from .controllers import appointments
from .controllers import therapists
from .controllers import reviews
from .controllers import roles
from .controllers import images
from .controllers import applications


api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(appointments.router)
api_router.include_router(reviews.router)
api_router.include_router(roles.router)
api_router.include_router(therapists.router)
api_router.include_router(images.router)
api_router.include_router(applications.router)
