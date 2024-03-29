from fastapi import APIRouter, UploadFile
from sqlmodel import delete

from app import crud
from app.api.deps import DocumentDep, DocumentSetDep, SessionDep
from app.models import Document, DocumentOut, DocumentSetCreate, DocumentSetOut, Page


router = APIRouter()


@router.post("/", response_model=DocumentSetOut)
def create_document_set(session: SessionDep, docset_create: DocumentSetCreate):
    return crud.create_document_set(session=session, docset_create=docset_create)


@router.delete("/{docset_id}")
def delete_document_set(session: SessionDep, docset: DocumentSetDep):
    for doc in docset.documents:
        session.exec(delete(Page).where(Page.document_id == doc.id))
        session.delete(doc)
    session.delete(docset)
    session.commit()
    # TODO: delete files under the path of the document set


@router.get("/", response_model=list[DocumentSetOut])
def list_document_sets(session: SessionDep):
    return crud.list_document_sets(session=session)


@router.post("/{docset_id}", response_model=list[DocumentOut])
def upload_documents(
    session: SessionDep, docset: DocumentSetDep, files: list[UploadFile]
):
    for file in files:
        docset.documents.append(Document(name=file.filename))
    session.add(docset)
    session.commit()
    # TODO: save document to fs
    # TODO: splite to pages, create pages and vectorize them


@router.get("/{docset_id}/docs", response_model=list[DocumentOut])
def list_documents(docset: DocumentSetDep):
    return docset.documents


@router.get("/{docset_id}/docs/{doc_id}")
def download_document(session: SessionDep, doc: DocumentDep):
    # TODO: get path of document and retun
    pass


@router.delete("/{docset_id}/docs/{doc_id}")
def delete_document(session: SessionDep, doc: DocumentDep):
    # TODO: remove document pages from vectorstore
    session.exec(delete(Page).where(Page.document_id == doc.id))
    session.delete(doc)
    session.commit()
