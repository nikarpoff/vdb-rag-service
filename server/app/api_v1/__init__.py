from fastapi import APIRouter
from app.api_v1.endpoints import documents, search, chat

router = APIRouter()

router.include_router(documents.router)
router.include_router(search.router)
router.include_router(chat.router)
