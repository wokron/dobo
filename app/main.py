from fastapi import FastAPI

from app.api.main import api_router

app = FastAPI(
    title="Dobo",
    description="Document chat bot powered by LLMs and Retrieval-Augmented Generation (RAG)",
)


app.include_router(api_router)
