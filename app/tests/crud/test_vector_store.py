from sqlmodel import Session
from langchain_core.documents import Document as PagedDocument
from langchain_community.vectorstores import Chroma

from app.core import llm
from app.crud import (
    _save_pages_to_vectorstore,
    _remove_from_vectorstore,
)
from app.models import Document
from app.tests.utils.document import create_random_document
from app.tests.utils.document_set import create_random_document_set
from app.tests.utils.utils import get_random_lower_string


def test_create_pages_and_vectors(session: Session):
    doc = create_random_document(session)
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


def test_delete_vectors(session: Session):
    docset = create_random_document_set(session)

    docs = [
        Document(name=get_random_lower_string(), document_set=docset) for _ in range(2)
    ]
    session.add_all(docs)
    session.commit()

    doc1, doc2 = docs

    paged_docs = [
        PagedDocument(page_content=content) for content in ["page1", "page2", "page3"]
    ]

    vectorstore = Chroma(
        persist_directory=str(docset.get_vectorstore_dir()),
        embedding_function=llm.embeddings,
    )

    _save_pages_to_vectorstore(
        session=session,
        doc=doc1,
        paged_docs=paged_docs,
    )

    assert vectorstore._collection.count() == 3

    _save_pages_to_vectorstore(
        session=session,
        doc=doc2,
        paged_docs=paged_docs,
    )

    assert vectorstore._collection.count() == 6

    _remove_from_vectorstore(doc=doc2)

    assert vectorstore._collection.count() == 3

    _remove_from_vectorstore(doc=doc1)

    assert vectorstore._collection.count() == 0
