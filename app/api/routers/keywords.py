from fastapi import APIRouter

from app import crud
from app.api.deps import KeywordCreateDep, KeywordDep, SessionDep
from app.models import KeywordOut


router = APIRouter()


@router.post("/", response_model=KeywordOut)
def create_keyword(session: SessionDep, keyword_create: KeywordCreateDep):
    db_keyword = crud.create_keyword(session, keyword_create)
    return db_keyword


@router.get("/", response_model=list[KeywordOut])
def list_keywords(session: SessionDep):
    return crud.list_keywords(session)


@router.delete("/{keyword_id}")
def delete_keyword(session: SessionDep, keyword: KeywordDep):
    crud.delete_keyword(session, keyword)
