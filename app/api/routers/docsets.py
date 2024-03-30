from pathlib import Path
import shutil
from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse
from sqlmodel import delete, select

from app import crud
from app.api.deps import DocumentDep, DocumentSetDep, SessionDep
from app.core.config import settings
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
    db_docset.get_save_path().mkdir(parents=True, exist_ok=True)
    return db_docset


@router.delete("/{docset_id}")
def delete_document_set(session: SessionDep, docset: DocumentSetDep):
    session.exec(delete(Document).where(Document.document_set_id == docset.id))
    session.delete(docset)
    session.commit()
    # delete files under the path of the document set
    shutil.rmtree(docset.get_save_path())


@router.get("/", response_model=list[DocumentSetOut])
def list_document_sets(session: SessionDep):
    return session.exec(select(DocumentSet)).all()


@router.post("/{docset_id}/docs", response_model=list[DocumentOut])
def upload_documents(
    session: SessionDep, docset: DocumentSetDep, files: list[UploadFile]
):
    new_docs: list[Document] = []
    for file in files:
        doc = Document(name=file.filename)
        docset.documents.append(doc)
        new_docs.append(doc)
    session.add(docset)
    session.commit()

    # save document to fs
    for file, doc in zip(files, new_docs):
        doc.get_save_path().write_bytes(file.file.read())
        # split document into pages, create pages and vectorize them
        crud.load_document_to_vector_store(session=session, doc=doc)

    return new_docs


@router.get("/{docset_id}/docs", response_model=list[DocumentOut])
def list_documents(docset: DocumentSetDep):
    return docset.documents
