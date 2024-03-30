from sqlmodel import Session
from langchain_core.documents import Document as PagedDocument
from langchain_community.vectorstores import Chroma

from app.core import llm
from app.crud import (
    add_paged_documents,
    remove_document_from_vector_store,
)
from app.models import Document


def test_create_pages_and_vectors(session: Session, doc: Document):
    paged_docs = [
        PagedDocument(page_content=content) for content in ["page1", "page2", "page3"]
    ]
    add_paged_documents(
        session=session,
        doc=doc,
        paged_docs=paged_docs,
    )

    vector_store = Chroma(
        persist_directory=str(doc.document_set.get_vector_store_path()),
        embedding_function=llm.embeddings,
    )
    assert vector_store._collection.count() == 3


def test_delete_vectors(session: Session, docset):
    doc2 = Document(name="doc2", document_set=docset)
    session.add(doc2)
    session.commit()

    paged_docs2 = [
        PagedDocument(page_content=content) for content in ["page1", "page2", "page3"]
    ]

    add_paged_documents(
        session=session,
        doc=doc2,
        paged_docs=paged_docs2,
    )

    vector_store = Chroma(
        persist_directory=str(doc2.document_set.get_vector_store_path()),
        embedding_function=llm.embeddings,
    )
    assert vector_store._collection.count() == 6

    remove_document_from_vector_store(doc=doc2)

    assert vector_store._collection.count() == 3
