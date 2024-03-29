from pathlib import Path

from sqlmodel import Session, select
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document as PagedDocument
from langchain_community.vectorstores import Chroma

from app.models import (
    Chat,
    ChatCreate,
    Document,
    DocumentSet,
    DocumentSetCreate,
    Page,
)
from app.core import llm


def create_document_set(*, session: Session, docset_create: DocumentSetCreate):
    db_docset = DocumentSet.model_validate(docset_create)
    session.add(db_docset)
    session.commit()
    session.refresh(db_docset)
    return db_docset


def create_chat(*, session: Session, chat_create: ChatCreate):
    db_chat = Chat.model_validate(chat_create)
    session.add(db_chat)
    session.commit()
    session.refresh(db_chat)
    return db_chat


def create_pages_and_vectors(*, session: Session, doc: Document):
    vector_store_path: Path = doc.document_set.get_vector_store_path()
    paged_docs: list[PagedDocument] = PyMuPDFLoader(doc.get_save_path()).load()

    db_pages: list[Page] = []
    for _ in range(len(paged_docs)):
        db_pages.append(Page(document_id=doc.id))
    session.add_all(db_pages)
    session.commit()
    ids = [page.id for page in db_pages]

    Chroma.from_documents(
        paged_docs,
        llm.embeddings,
        ids=ids,
        persist_directory=vector_store_path,
    )


def delete_vectors(*, doc: Document):
    vector_store_path: Path = doc.document_set.get_vector_store_path()
    ids = [page.id for page in doc.pages]

    vector_store = Chroma(
        persist_directory=vector_store_path,
        embedding_function=llm.embeddings,
    )
    vector_store._collection.delete(ids=ids)
