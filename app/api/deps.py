from functools import lru_cache
from importlib import import_module
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlmodel import Session
from langchain_core.runnables import Runnable

from app import crud
from app.core.config import settings
from app.core.db import engine
from app.models import Chat, Document, DocumentSet


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


def get_document(session: SessionDep, docset_id: int, doc_id: int):
    db_doc = session.get(Document, (doc_id, docset_id))
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


@lru_cache
def get_chain() -> Runnable:
    llm_cls = getattr(
        import_module("langchain_community.chat_models"), settings.llm.class_name
    )
    llm = llm_cls(**settings.llm.config)
    return crud.create_chain(llm)


ChainDep = Annotated[Runnable, Depends(get_chain)]
