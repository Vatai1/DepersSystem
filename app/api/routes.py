import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.core import settings, logger
from app.services.model_manager import model_manager
from app.services.text_pipeline import depersonalize_text
from app.services.file_pipeline import process_file

router = APIRouter(prefix="/api")


class TextRequest(BaseModel):
    text: str
    mode: str = "replace"


@router.get("/health")
async def health():
    return {"status": "ok", "model_loaded": model_manager.is_loaded}


@router.get("/model")
async def get_model_info():
    return {
        "name": settings.model_name,
        "loaded": model_manager.is_loaded,
        "device": settings.device,
        "languages": ["ru", "en"],
    }


@router.post("/depersonalize/text")
async def depersonalize_text_endpoint(req: TextRequest):
    result = depersonalize_text(req.text, req.mode)
    return result


@router.post("/depersonalize/file")
async def depersonalize_file_endpoint(
    file: UploadFile = File(...),
    mode: str = Form("replace"),
):
    os.makedirs(settings.data_dir, exist_ok=True)
    suffix = Path(file.filename or "file.txt").suffix
    with tempfile.NamedTemporaryFile(dir=settings.data_dir, suffix=suffix, delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = process_file(tmp_path, mode)
        return result
    finally:
        if not result.get("download_url", "").endswith(Path(tmp_path).name):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


@router.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(settings.data_dir, filename)
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    return FileResponse(
        file_path,
        filename=filename,
        media_type="application/octet-stream",
    )
