from pathlib import Path
import shutil

from fastapi import UploadFile
from sqlmodel import Session, delete
from langchain_core.documents import Document as PagedDocument
from langchain_core.messages import BaseMessage
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.runnables import Runnable

from app.core.config import settings
from app.models import (
    Chat,
    ChatCreate,
    Document,
    DocumentSet,
    DocumentSetCreate,
    MessageIn,
    MessageOut,
)
from app.core import llm


def create_document_set(session: Session, docset_create: DocumentSetCreate):
    db_docset = DocumentSet.model_validate(docset_create)
    session.add(db_docset)
    session.commit()
    session.refresh(db_docset)

    db_docset.get_save_path().mkdir(parents=True, exist_ok=True)
    db_docset.get_documents_path().mkdir(exist_ok=True)
    db_docset.get_vector_store_path().mkdir(exist_ok=True)
    return db_docset


def delete_document_set(session: Session, docset: DocumentSet):
    session.exec(delete(Document).where(Document.document_set_id == docset.id))
    session.delete(docset)
    session.commit()
    # delete files under the path of the document set
    shutil.rmtree(docset.get_save_path())


def create_document(session: Session, file: UploadFile, docset_id: int):
    db_doc = Document(name=file.filename, document_set_id=docset_id)
    session.add(db_doc)
    session.commit()

    # save document to fs
    db_doc.get_save_path().write_bytes(file.file.read())
    # split document into pages, create pages and vectorize them
    load_document_to_vector_store(session, db_doc)

    return db_doc


def delete_document(session: Session, doc: Document):
    # remove pages from vector store
    remove_document_from_vector_store(doc=doc)

    session.delete(doc)
    session.commit()
    # delete document from fs
    doc.get_save_path().unlink()


def create_chat(session: Session, chat_create: ChatCreate):
    db_chat = Chat.model_validate(chat_create)
    session.add(db_chat)
    session.commit()
    session.refresh(db_chat)
    return db_chat


def post_message_in_chat(chat: Chat, message: MessageIn):
    # invoke the llm chain and return llm's answer
    result = llm.chain.invoke(
        {"input": message.content},
        config={
            "configurable": {
                "session_id": chat.id,
                "vectorstore": str(chat.document_set.get_vector_store_path()),
            }
        },
    )
    return MessageOut(role="ai", content=result["answer"])


def delete_chat(session: Session, chat: Chat):
    session.delete(chat)
    session.commit()
    # delete chat history
    delete_chat_history(chat_id=chat.id)


def load_document_to_vector_store(session: Session, doc: Document):
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


def list_chat_history(*, chat_id: int):
    history = SQLChatMessageHistory(
        session_id=chat_id,
        connection_string=settings.memory_url,
    )
    messages: list[BaseMessage] = history.messages
    messages_out: list[MessageOut] = []
    for message in messages:
        messages_out.append(MessageOut(role=message.type, content=message.content))

    return messages_out
