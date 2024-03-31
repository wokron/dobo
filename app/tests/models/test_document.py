from sqlmodel import Session, select

from app.models import Document
from app.tests.utils.document import create_random_document
from app.tests.utils.document_set import create_random_document_set
from app.tests.utils.utils import get_random_lower_string


def test_create_document(session: Session):
    docset = create_random_document_set(session)
    db_doc = Document(name=get_random_lower_string(), document_set=docset)
    session.add(db_doc)
    session.commit()
    assert db_doc.id != None


def test_get_document(session: Session):
    db_doc = create_random_document(session)

    doc_id = db_doc.id
    db_doc2 = session.get(Document, doc_id)
    assert db_doc.model_dump() == db_doc2.model_dump()


def test_delete_document(session: Session):
    db_doc = create_random_document(session)

    session.delete(db_doc)
    session.commit()
    db_doc = session.exec(select(Document).where(Document.name == db_doc.name)).first()
    assert db_doc == None
