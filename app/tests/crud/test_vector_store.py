from sqlmodel import Session
from langchain_core.documents import Document as PagedDocument
from langchain_community.vectorstores import Chroma

from app.core import llm
from app.crud import (
    create_pages_and_vectors,
    delete_vectors,
)
from app.models import Document


def test_create_pages_and_vectors(session: Session, doc: Document):
    paged_docs = [
        PagedDocument(page_content=content) for content in ["page1", "page2", "page3"]
    ]
    create_pages_and_vectors(
        session=session,
        doc_id=doc.id,
        paged_docs=paged_docs,
        vector_store_path="./chroma",
    )

    vector_store = Chroma(
        persist_directory="./chroma",
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

    create_pages_and_vectors(
        session=session,
        doc_id=doc2.id,
        paged_docs=paged_docs2,
        vector_store_path="./chroma",
    )

    vector_store = Chroma(
        persist_directory="./chroma",
        embedding_function=llm.embeddings,
    )
    assert vector_store._collection.count() == 6

    ids = [str(page.id) for page in doc2.pages]

    delete_vectors(ids=ids, vector_store_path="./chroma")

    assert vector_store._collection.count() == 3
