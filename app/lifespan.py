from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import Session

from app import crud
from app.core import ac, db


@asynccontextmanager
async def lifespan(app: FastAPI):
    with Session(db.engine) as session:
        ac.init_automaton(crud.list_keywords(session))
    yield
