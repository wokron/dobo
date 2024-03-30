from sqlmodel import Session
from app import crud
from app.models import Document
from app.tests.utils.document_set import create_random_document_set
from app.tests.utils.utils import get_random_pdf


def create_random_document(session: Session):
    filename, data = get_random_pdf()
    docset = create_random_document_set(session)
    doc = Document(name=filename, document_set_id=docset.id)
    session.add(doc)
    session.commit()
    doc.get_save_path().write_bytes(data)
    crud.load_document_to_vector_store(session=session, doc=doc)
