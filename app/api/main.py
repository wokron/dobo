from fastapi import APIRouter

from app.api.routers import docsets, chats, docs

api_router = APIRouter()
api_router.include_router(docsets.router, prefix="/docsets")
api_router.include_router(chats.router, prefix="/chats")
api_router.include_router(docs.router, prefix="/docs")
