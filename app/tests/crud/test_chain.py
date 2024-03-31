from langchain_community.chat_models import FakeListChatModel
from langchain_core.documents import Document as PagedDocument
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from sqlmodel import Session


from app import crud
from app.api.deps import get_chain
from app.models import Document
from app.core.config import settings


def test_create_chain(session: Session, doc: Document):
    memory: BaseChatMessageHistory = SQLChatMessageHistory(
        session_id=3,
        connection_string=settings.memory_url,
    )

    memory.clear()

    paged_docs = [
        PagedDocument(page_content=content) for content in ["apple", "banana", "water"]
    ]
    crud.add_paged_documents(
        session=session,
        doc=doc,
        paged_docs=paged_docs,
    )

    llm = FakeListChatModel(responses=["Sorry", "Something about apple", "I don't know"])

    chain = crud.create_chain(llm)

    result = chain.invoke(
        {"input": "give me apple"},
        config={
            "configurable": {
                "session_id": 3,
                "vectorstore": str(doc.document_set.get_vector_store_path()),
            }
        },
    )

    assert result["answer"] == "Sorry"

    result = chain.invoke(
        {"input": "give me apple"},
        config={
            "configurable": {
                "session_id": 3,
                "vectorstore": str(doc.document_set.get_vector_store_path()),
            }
        },
    )

    assert result["answer"] == "I don't know"


def test_dynamic_import():
    _ = get_chain()
