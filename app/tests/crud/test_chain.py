from langchain_core.documents import Document as PagedDocument
from langchain_community.chat_models import FakeListChatModel
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from sqlmodel import Session


from app import crud
from app.models import Document
from app.core.config import settings
from app.core import llm
from app.tests.utils.document_set import create_random_document_set
from app.tests.utils.utils import get_random_lower_string


def test_create_chain(session: Session):
    docset = create_random_document_set(session)
    doc = Document(name=get_random_lower_string(), document_set=docset)
    session.add(doc)
    session.commit()

    memory: BaseChatMessageHistory = SQLChatMessageHistory(
        session_id=3,
        connection_string=settings.memory_url,
    )

    memory.clear()

    paged_docs = [
        PagedDocument(page_content=content) for content in ["apple", "banana", "water"]
    ]
    crud._save_pages_to_vectorstore(
        session=session,
        doc=doc,
        paged_docs=paged_docs,
    )

    model = FakeListChatModel(
        responses=["Sorry", "Something about apple", "I don't know"]
    )

    chain = llm._create_chain(model)

    result = chain.invoke(
        {"input": "give me apple", "keywords": {}},
        config={
            "configurable": {
                "session_id": 3,
                "vectorstore": str(doc.document_set.get_vectorstore_dir()),
            }
        },
    )

    assert result["answer"] == "Sorry"

    result = chain.invoke(
        {"input": "give me apple", "keywords": {}},
        config={
            "configurable": {
                "session_id": 3,
                "vectorstore": str(doc.document_set.get_vectorstore_dir()),
            }
        },
    )

    assert result["answer"] == "I don't know"


def test_dynamic_import():
    _ = llm._create_chain(llm.model)
