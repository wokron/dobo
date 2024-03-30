import pytest
from sqlmodel import Session, select, delete

from app.models import Document, Page, DocumentSet


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


def test_add_pages(session: Session, docset: DocumentSet):
    db_doc = Document(name="doc3", document_set=docset)
    session.add(db_doc)
    session.commit()

    assert len(db_doc.pages) == 0

    page_num = 10
    new_pages = []
    for _ in range(page_num):
        new_pages.append(Page(document_id=db_doc.id))

    session.add_all(new_pages)
    session.commit()

    assert len(db_doc.pages) == 10
    for page in db_doc.pages:
        assert page.id != None

    new_pages = []
    for _ in range(page_num):
        new_page = Page()
        new_pages.append(new_page)
        db_doc.pages.append(new_page)

    session.add(db_doc)
    session.commit()

    assert len(db_doc.pages) == 20


def test_delete_document(session: Session):
    db_doc = session.exec(select(Document).where(Document.name == "doc3")).one()
    assert len(db_doc.pages) == 20

    session.exec(delete(Page).where(Page.document_id == db_doc.id))
    session.commit()
    session.flush(db_doc)
    assert len(db_doc.pages) == 0

    session.delete(db_doc)
    session.commit()
    db_doc = session.exec(select(Document).where(Document.name == "doc3")).first()
    assert db_doc == None
