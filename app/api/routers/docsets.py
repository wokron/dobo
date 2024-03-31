from fastapi import APIRouter, UploadFile
from sqlmodel import select

from app import crud
from app.api.deps import DocumentSetDep, SessionDep
from app.models import (
    Document,
    DocumentOut,
    DocumentSet,
    DocumentSetCreate,
    DocumentSetOut,
)


router = APIRouter()


@router.post("/", response_model=DocumentSetOut)
def create_document_set(session: SessionDep, docset_create: DocumentSetCreate):
    db_docset = crud.create_document_set(session=session, docset_create=docset_create)
    return db_docset


@router.delete("/{docset_id}")
def delete_document_set(session: SessionDep, docset: DocumentSetDep):
    crud.delete_document_set(session, docset)


@router.get("/", response_model=list[DocumentSetOut])
def list_document_sets(session: SessionDep):
    return session.exec(select(DocumentSet)).all()


@router.post("/{docset_id}/docs", response_model=list[DocumentOut])
def upload_documents(
    session: SessionDep,
    docset: DocumentSetDep,
    files: list[UploadFile],
):
    new_docs: list[Document] = []
    for file in files:
        new_docs.append(crud.create_document(session, file, docset.id))

    return new_docs


@router.get("/{docset_id}/docs", response_model=list[DocumentOut])
def list_documents(docset: DocumentSetDep):
    return docset.documents
