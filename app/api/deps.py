from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.db import engine
from app.models import (
    Chat,
    ChatCreate,
    Document,
    DocumentSet,
    DocumentSetCreate,
    Keyword,
    KeywordCreate,
)


def get_db():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]


def get_document_set(session: SessionDep, docset_id: int):
    db_docset = session.get(DocumentSet, docset_id)
    if db_docset == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="DocumentSet not found"
        )
    return db_docset


DocumentSetDep = Annotated[DocumentSet, Depends(get_document_set)]


def validate_document_set(session: SessionDep, docset_create: DocumentSetCreate):
    db_docset = session.exec(
        select(DocumentSet).where(DocumentSet.name == docset_create.name)
    ).first()
    if db_docset != None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Document set named "{docset_create.name}" already exists',
        )
    return docset_create


DocumentSetCreateDep = Annotated[DocumentSetCreate, Depends(validate_document_set)]


def get_document(session: SessionDep, doc_id: int):
    db_doc = session.get(Document, doc_id)
    if db_doc == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
    return db_doc


DocumentDep = Annotated[Document, Depends(get_document)]


def get_chat(session: SessionDep, chat_id: int):
    db_chat = session.get(Chat, chat_id)
    if db_chat == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found"
        )
    return db_chat


ChatDep = Annotated[Chat, Depends(get_chat)]


def validate_chat(session: SessionDep, chat_create: ChatCreate):
    db_chat = session.exec(select(Chat).where(Chat.name == chat_create.name)).first()
    if db_chat != None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Chat named "{chat_create.name}" already exists',
        )
    return chat_create


ChatCreateDep = Annotated[ChatCreate, Depends(validate_chat)]


def get_keyword(session: SessionDep, keyword_id: int):
    db_keyword = session.get(Keyword, keyword_id)
    if db_keyword == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Keyword not found"
        )
    return db_keyword


KeywordDep = Annotated[Keyword, Depends(get_keyword)]


def validate_keyword(session: SessionDep, keyword_create: KeywordCreate):
    db_keyword = session.exec(
        select(Keyword).where(Keyword.keyword == keyword_create.keyword)
    ).first()
    if db_keyword != None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Keyowrd "{keyword_create.keyword}" already exists',
        )
    return keyword_create


KeywordCreateDep = Annotated[KeywordCreate, Depends(validate_keyword)]
