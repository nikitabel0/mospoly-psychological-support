import os
from mimetypes import guess_type

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(tags=["images"])

IMAGE_DIR = "images"  # Папка с изображениями


@router.get("/image/{filename}")
async def get_dynamic_image(filename: str):
    file_path = os.path.join("/srv/images", filename)
    if not os.path.exists(file_path):
        return {"error": "Файл не найден"}
    media_type = guess_type(file_path)[0] or "application/octet-stream"
    return FileResponse(file_path, media_type=media_type)
