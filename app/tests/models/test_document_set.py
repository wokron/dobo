from sqlmodel import Session, delete

from app.models import Document, DocumentSet
from app.tests.utils.document_set import create_random_document_set
from app.tests.utils.utils import get_random_lower_string


def test_create_document_set(session: Session):
    db_docset = DocumentSet(name=get_random_lower_string())
    session.add(db_docset)
    session.commit()
    assert db_docset.id != None


def test_get_document_set(session: Session):
    db_docset = create_random_document_set(session)

    docset_id = db_docset.id
    db_docset2 = session.get(DocumentSet, docset_id)
    assert db_docset.model_dump() == db_docset2.model_dump()


def test_add_document(session: Session):
    db_docset = create_random_document_set(session)

    db_doc = Document(name=get_random_lower_string(), document_set_id=db_docset.id)
    session.add(db_doc)
    session.commit()
    assert db_doc.id != None
    assert len(db_docset.documents) == 1
    assert db_docset.documents[0].model_dump() == db_doc.model_dump()

    db_doc2 = Document(name=get_random_lower_string())
    db_docset.documents.append(db_doc2)
    session.add(db_doc2)
    session.commit()
    assert db_doc2.id != None
    assert len(db_docset.documents) == 2
