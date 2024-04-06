from fastapi import APIRouter
from sqlmodel import select

from app import crud
from app.api.deps import KeywordDep, SessionDep
from app.models import Keyword, KeywordCreate, KeywordOut


router = APIRouter()


@router.post("/", response_model=KeywordOut)
def create_keyword(session: SessionDep, keyword_create: KeywordCreate):
    db_keyword = crud.create_keyword(session, keyword_create)
    return db_keyword


@router.get("/", response_model=list[KeywordOut])
def list_keywords(session: SessionDep):
    return session.exec(select(Keyword)).all()


@router.delete("/{keyword_id}")
def delete_keyword(session: SessionDep, keyword: KeywordDep):
    crud.delete_keyword(session, keyword)
