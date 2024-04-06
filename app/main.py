from fastapi import FastAPI

from app.api.main import api_router
from app.lifespan import lifespan


app = FastAPI(
    title="Dobo",
    description="Document chat bot powered by LLMs and Retrieval-Augmented Generation (RAG)",
    lifespan=lifespan,
)


app.include_router(api_router)
