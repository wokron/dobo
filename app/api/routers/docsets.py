from fastapi import APIRouter, HTTPException, UploadFile, status
from sqlmodel import select

from app import crud
from app.api.deps import DocumentSetCreateDep, DocumentSetDep, SessionDep
from app.models import (
    Document,
    DocumentOut,
    DocumentSet,
    DocumentSetOut,
)


router = APIRouter()


@router.post("/", response_model=DocumentSetOut)
def create_document_set(session: SessionDep, docset_create: DocumentSetCreateDep):
    db_docset = crud.create_document_set(session=session, docset_create=docset_create)
    return db_docset


@router.delete("/{docset_id}")
def delete_document_set(session: SessionDep, docset: DocumentSetDep):
    crud.delete_document_set(session, docset)


@router.get("/", response_model=list[DocumentSetOut])
def list_document_sets(session: SessionDep):
    return session.exec(select(DocumentSet)).all()


@router.get("/name/{docset_name}", response_model=DocumentSetOut)
def get_document_set_by_name(session: SessionDep, docset_name: str):
    db_docset = session.exec(
        select(DocumentSet).where(DocumentSet.name == docset_name)
    ).first()
    if db_docset == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="DocumentSet not found"
        )
    return db_docset


@router.post("/{docset_id}/docs", response_model=list[DocumentOut], tags=["docs"])
def upload_documents(
    session: SessionDep,
    docset: DocumentSetDep,
    files: list[UploadFile],
):
    new_docs: list[Document] = []
    for file in files:
        new_docs.append(crud.create_document_from_upload(session, file, docset.id))

    return new_docs


@router.get("/{docset_id}/docs", response_model=list[DocumentOut], tags=["docs"])
def list_documents(docset: DocumentSetDep):
    return docset.documents
