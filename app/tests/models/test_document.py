import pytest
from sqlmodel import Session, select, delete

from app.models import Document, DocumentSet


def test_create_document(session: Session, docset: DocumentSet):
    db_doc = Document(name="doc1", document_set=docset)
    session.add(db_doc)
    session.commit()
    assert db_doc.id != None


def test_get_document(session: Session, docset: DocumentSet):
    db_doc = Document(name="doc2", document_set=docset)
    session.add(db_doc)
    session.commit()

    doc_id = db_doc.id
    db_doc2 = session.get(Document, doc_id)
    assert db_doc.model_dump() == db_doc2.model_dump()


def test_delete_document(session: Session):
    db_doc = session.exec(select(Document).where(Document.name == "doc2")).one()

    session.delete(db_doc)
    session.commit()
    db_doc = session.exec(select(Document).where(Document.name == "doc2")).first()
    assert db_doc == None
