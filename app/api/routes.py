import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.core import settings
from app.core.config import MODEL_REGISTRY
from app.services.file_pipeline import process_file
from app.services.mapping_store import mapping_store
from app.services.model_manager import model_manager
from app.services.text_pipeline import depersonalize_text

router = APIRouter(prefix="/api")


class TextRequest(BaseModel):
    text: str
    mode: str = "replace"


class SwitchModelRequest(BaseModel):
    model_name: str


class RepersonalizeTextRequest(BaseModel):
    text: str
    key: str


@router.get("/health")
async def health():
    return {"status": "ok", "model_loaded": model_manager.is_loaded}


@router.get("/model")
async def get_model_info():
    return model_manager.get_info()


@router.get("/models")
async def list_models():
    current = model_manager.model_name
    models = []
    for name, info in MODEL_REGISTRY.items():
        models.append(
            {
                "model_name": name,
                "display_name": info.get("display_name", name),
                "description": info.get("description", ""),
                "size": info.get("size", ""),
                "scheme": info.get("scheme", "standard"),
                "is_active": name == current,
            }
        )
    return {"models": models, "active": current}


@router.post("/models/switch")
async def switch_model(req: SwitchModelRequest):
    if req.model_name not in MODEL_REGISTRY:
        return {"error": f"Unknown model: {req.model_name}"}
    if req.model_name == model_manager.model_name and model_manager.is_loaded:
        return {"status": "already_active", "model": model_manager.get_info()}
    model_manager.load(req.model_name)
    return {"status": "switched", "model": model_manager.get_info()}


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


@router.post("/repersonalize/text")
async def repersonalize_text_endpoint(req: RepersonalizeTextRequest):
    restored = mapping_store.repersonalize_text(req.text, req.key)
    if restored is None:
        return {"error": "Key not found or expired"}
    return {"original_text": restored, "key": req.key}


@router.post("/repersonalize/file")
async def repersonalize_file_endpoint(
    file: UploadFile = File(...),
    key: str = Form(...),
):
    os.makedirs(settings.data_dir, exist_ok=True)
    suffix = Path(file.filename or "file.txt").suffix
    with tempfile.NamedTemporaryFile(dir=settings.data_dir, suffix=suffix, delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()

        restored = mapping_store.repersonalize_text(text, key)
        if restored is None:
            return {"error": "Key not found or expired"}

        out_path = tmp_path.replace(suffix, f"_repersonalized{suffix}")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(restored)

        return {
            "original_text": restored,
            "key": key,
            "download_url": f"/api/download/{os.path.basename(out_path)}",
        }
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


@router.get("/vault")
async def list_vault_keys():
    return {"keys": mapping_store.list_keys()}


@router.delete("/vault/{key}")
async def delete_vault_key(key: str):
    deleted = mapping_store.delete(key)
    if not deleted:
        return {"error": "Key not found"}
    return {"status": "deleted"}


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
