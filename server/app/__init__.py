from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api_v1 import router as api_v1_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="RAG-SSW API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_v1_router, prefix="/v1")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
