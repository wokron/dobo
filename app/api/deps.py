from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlmodel import Session
from app.core.db import engine
from app.models import Document, DocumentSet


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
