from fastapi import APIRouter

from app.api.routers import docsets, chats, docs, keywords

api_router = APIRouter()
api_router.include_router(docsets.router, prefix="/docsets", tags=["docsets"])
api_router.include_router(chats.router, prefix="/chats", tags=["chats"])
api_router.include_router(docs.router, prefix="/docs", tags=["docs"])
api_router.include_router(keywords.router, prefix="/keywords", tags=["keywords"])
