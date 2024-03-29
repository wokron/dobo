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
    Page,
)


router = APIRouter()


@router.post("/", response_model=DocumentSetOut)
def create_document_set(session: SessionDep, docset_create: DocumentSetCreate):
    db_docset = crud.create_document_set(session=session, docset_create=docset_create)
    db_docset.get_save_path().mkdir(parents=True, exist_ok=True)
    return db_docset


@router.delete("/{docset_id}")
def delete_document_set(session: SessionDep, docset: DocumentSetDep):
    for doc in docset.documents:
        session.exec(delete(Page).where(Page.document_id == doc.id))
        session.delete(doc)
    session.delete(docset)
    session.commit()
    # delete files under the path of the document set
    shutil.rmtree(docset.get_save_path())


@router.get("/", response_model=list[DocumentSetOut])
def list_document_sets(session: SessionDep):
    return session.exec(select(DocumentSet)).all()


@router.post("/{docset_id}", response_model=list[DocumentOut])
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
        crud.create_pages_and_vectors(session=session, doc=doc)


@router.get("/{docset_id}/docs", response_model=list[DocumentOut])
def list_documents(docset: DocumentSetDep):
    return docset.documents


@router.get("/{docset_id}/docs/{doc_id}")
def download_document(session: SessionDep, doc: DocumentDep):
    # get path of document and retun
    doc_path = doc.get_save_path()
    return FileResponse(path=doc_path, filename=doc.name)


@router.delete("/{docset_id}/docs/{doc_id}")
def delete_document(session: SessionDep, doc: DocumentDep):
    # remove pages from vector store
    crud.delete_vectors(doc=doc)
    session.exec(delete(Page).where(Page.document_id == doc.id))
    session.delete(doc)
    session.commit()
    # delete document from fs
    doc.get_save_path().unlink()
