from sqlmodel import Session, select
from app.models import (
    Chat,
    ChatCreate,
    Document,
    DocumentSet,
    DocumentSetCreate,
)


def create_document_set(*, session: Session, docset_create: DocumentSetCreate):
    db_docset = DocumentSet.model_validate(docset_create)
    session.add(db_docset)
    session.commit()
    session.refresh(db_docset)
    return db_docset


def delete_document_set(*, session: Session, docset_id: int):
    db_docset = session.get(DocumentSet, docset_id)
    if db_docset == None:
        return
    session.delete(db_docset)
    session.commit()
    # TODO: delete files under the path of the document set


def list_document_sets(*, session: Session):
    return session.exec(select(Document)).all()


def create_document(
    *, session: Session, doc_name: str, doc_data: bytes, docset_id: int
):
    db_doc = Document(name=doc_name, document_set_id=docset_id)
    session.add(db_doc)
    session.commit()
    session.refresh(db_doc)
    # TODO: save document to fs
    # TODO: splite to pages, create pages and vectorize them
    return db_doc


def delete_document(*, session: Session, docset_id: int, doc_id: int):
    db_doc = session.get(Document, (doc_id, docset_id))
    if db_doc == None:
        return
    session.delete(db_doc)
    session.commit()
    # TODO: delete files under the path of the document


def create_chat(*, session: Session, chat_create: ChatCreate):
    db_chat = Chat.model_validate(chat_create)
    session.add(db_chat)
    session.commit()
    session.refresh(db_chat)
    return db_chat


def delete_chat(*, session: Session, chat_id: int):
    db_doc = session.get(Document, chat_id)
    if db_doc == None:
        return
    session.delete(db_doc)
    session.commit()
