from sqlmodel import Session
from langchain_core.documents import Document as PagedDocument
from langchain_community.vectorstores import Chroma

from app.core import llm
from app.crud import (
    _save_pages_to_vectorstore,
    _remove_from_vectorstore,
)
from app.models import Document


def test_create_pages_and_vectors(session: Session, doc: Document):
    paged_docs = [
        PagedDocument(page_content=content) for content in ["page1", "page2", "page3"]
    ]
    _save_pages_to_vectorstore(
        session=session,
        doc=doc,
        paged_docs=paged_docs,
    )

    vectorstore = Chroma(
        persist_directory=str(doc.document_set.get_vectorstore_dir()),
        embedding_function=llm.embeddings,
    )
    assert vectorstore._collection.count() == 3


def test_delete_vectors(session: Session, docset):
    doc2 = Document(name="doc2", document_set=docset)
    session.add(doc2)
    session.commit()

    paged_docs2 = [
        PagedDocument(page_content=content) for content in ["page1", "page2", "page3"]
    ]

    _save_pages_to_vectorstore(
        session=session,
        doc=doc2,
        paged_docs=paged_docs2,
    )

    vectorstore = Chroma(
        persist_directory=str(doc2.document_set.get_vectorstore_dir()),
        embedding_function=llm.embeddings,
    )
    assert vectorstore._collection.count() == 6

    _remove_from_vectorstore(doc=doc2)

    assert vectorstore._collection.count() == 3
