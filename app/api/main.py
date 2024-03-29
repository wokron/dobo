from fastapi import APIRouter

from app.api.routers import docsets

api_router = APIRouter()
api_router.include_router(docsets.router, prefix="/docsets")
