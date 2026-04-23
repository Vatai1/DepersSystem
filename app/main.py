import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.core import logger
from app.services.model_manager import model_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting DepersSys...")
    model_manager.load()
    yield
    logger.info("Shutting down DepersSys...")


app = FastAPI(
    title="DepersSys",
    description="Local AI-based data depersonalization system",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

static_dir = "frontend/dist"

if os.path.isdir(static_dir):
    from fastapi.responses import FileResponse

    app.mount("/assets", StaticFiles(directory=f"{static_dir}/assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(static_dir, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(static_dir, "index.html"))
