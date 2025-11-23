from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from mimetypes import guess_type

import os

router = APIRouter(tags=["images"])

IMAGE_DIR = os.getenv("IMAGE_DIR", "/srv/images")


@router.get("/image/{filename}")
async def get_dynamic_image(filename: str):
    """
    Получить изображение по имени файла.
    
    Этот эндпоинт намеренно сделан публичным (без авторизации),
    так как изображения используются для отображения фотографий психологов
    и должны быть доступны всем пользователям.
    """
    file_path = os.path.join(IMAGE_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    media_type = guess_type(file_path)[0] or "application/octet-stream"
    return FileResponse(file_path, media_type=media_type)
