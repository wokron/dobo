from fastapi import APIRouter
from fastapi.responses import FileResponse

from app import crud
from app.api.deps import DocumentDep, SessionDep


router = APIRouter()


@router.get("/{doc_id}")
def download_document(doc: DocumentDep):
    # get path of document and retun
    doc_path = doc.get_save_path()
    return FileResponse(path=doc_path, filename=doc.name)


@router.delete("/{doc_id}")
def delete_document(session: SessionDep, doc: DocumentDep):
    crud.delete_document(session, doc)
