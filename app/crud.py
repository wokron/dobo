from pathlib import Path

from sqlmodel import Session
from langchain_core.documents import Document as PagedDocument
from langchain_core.messages import BaseMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda, RunnableConfig
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.chat_message_histories import SQLChatMessageHistory


from app.core.config import settings
from app.models import (
    Chat,
    ChatCreate,
    Document,
    DocumentSet,
    DocumentSetCreate,
    MessageOut,
)
from app.core import llm


def create_document_set(*, session: Session, docset_create: DocumentSetCreate):
    db_docset = DocumentSet.model_validate(docset_create)
    session.add(db_docset)
    session.commit()
    session.refresh(db_docset)
    db_docset.get_save_path().mkdir(parents=True, exist_ok=True)
    return db_docset


def create_chat(*, session: Session, chat_create: ChatCreate):
    db_chat = Chat.model_validate(chat_create)
    session.add(db_chat)
    session.commit()
    session.refresh(db_chat)
    return db_chat


def load_document_to_vector_store(*, session: Session, doc: Document):
    paged_docs: list[PagedDocument] = PyMuPDFLoader(str(doc.get_save_path())).load()

    add_paged_documents(session=session, doc=doc, paged_docs=paged_docs)


def add_paged_documents(
    *,
    session: Session,
    doc: Document,
    paged_docs: list[PagedDocument],
):
    doc.page_num = len(paged_docs)
    session.add(doc)
    session.commit()

    ids = [f"doc{doc.id}_page{no}" for no in range(doc.page_num)]
    vector_store_path: Path = doc.document_set.get_vector_store_path()
    Chroma.from_documents(
        paged_docs,
        llm.embeddings,
        ids=ids,
        persist_directory=str(vector_store_path),
    )


def remove_document_from_vector_store(*, doc: Document):
    vector_store_path: Path = doc.document_set.get_vector_store_path()
    ids = [f"doc{doc.id}_page{no}" for no in range(doc.page_num)]

    vector_store = Chroma(
        persist_directory=str(vector_store_path),
        embedding_function=llm.embeddings,
    )
    vector_store._collection.delete(ids=ids)


def delete_chat_history(*, chat_id: int):
    history = SQLChatMessageHistory(
        session_id=chat_id,
        connection_string=settings.memory_url,
    )
    history.clear()


def get_chat_history(*, chat_id: int):
    history = SQLChatMessageHistory(
        session_id=chat_id,
        connection_string=settings.memory_url,
    )
    messages: list[BaseMessage] = history.messages
    messages_out: list[MessageOut] = []
    for message in messages:
        messages_out.append(MessageOut(role=message.type, content=message.content))

    return messages_out


def create_chain(model):
    def select_retriever(text: str, config: RunnableConfig):
        vectorstore = Chroma(
            persist_directory=config["configurable"]["vectorstore"],
            embedding_function=llm.embeddings,
        )
        return vectorstore.as_retriever()

    retriever = RunnableLambda(select_retriever)
    retriever_chain = create_history_aware_retriever(
        model, retriever, llm.RETRIEVER_PROMPT
    )
    document_chain = create_stuff_documents_chain(model, llm.ANSWER_PROMPT)
    retrieval_chain = create_retrieval_chain(retriever_chain, document_chain)

    retrieval_chain_with_chat_history = RunnableWithMessageHistory(
        retrieval_chain,
        lambda session_id: SQLChatMessageHistory(
            session_id=session_id, connection_string=settings.memory_url
        ),
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    return retrieval_chain_with_chat_history
