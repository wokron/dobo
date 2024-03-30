from sqlmodel import Session

from app.models import Document, DocumentSet


def test_create_document_set(session: Session):
    db_docset = DocumentSet(name="docset1")
    session.add(db_docset)
    session.commit()
    assert db_docset.id != None


def test_get_document_set(session: Session):
    db_docset = DocumentSet(name="docset2")
    session.add(db_docset)
    session.commit()

    docset_id = db_docset.id
    db_docset2 = session.get(DocumentSet, docset_id)
    assert db_docset.model_dump() == db_docset2.model_dump()


def test_add_document(session: Session):
    db_docset = DocumentSet(name="docset3")
    session.add(db_docset)
    session.commit()

    db_doc = Document(name="doc1", document_set_id=db_docset.id)
    session.add(db_doc)
    session.commit()
    assert db_doc.id != None
    assert len(db_docset.documents) == 1
    assert db_docset.documents[0].model_dump() == db_doc.model_dump()

    db_doc2 = Document(name="doc2")
    db_docset.documents.append(db_doc2)
    session.add(db_docset)
    session.commit()
    assert db_doc2.id != None
    assert len(db_docset.documents) == 2
