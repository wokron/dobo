from fastapi import APIRouter
from fastapi.responses import FileResponse
from sqlmodel import delete

from app import crud
from app.api.deps import DocumentDep, SessionDep
from app.models import Page


router = APIRouter()


@router.get("/{doc_id}")
def download_document(session: SessionDep, doc: DocumentDep):
    # get path of document and retun
    doc_path = doc.get_save_path()
    return FileResponse(path=doc_path, filename=doc.name)


@router.delete("/{doc_id}")
def delete_document(session: SessionDep, doc: DocumentDep):
    # remove pages from vector store
    crud.remove_document_from_vector_store(doc=doc)
    session.exec(delete(Page).where(Page.document_id == doc.id))
    session.delete(doc)
    session.commit()
    # delete document from fs
    doc.get_save_path().unlink()
