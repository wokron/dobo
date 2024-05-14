from pathlib import Path
import shutil

from fastapi import UploadFile, HTTPException, status
from sqlmodel import Session, col, delete, select
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
    DocumentOut,
    DocumentOutWithPage,
    DocumentSet,
    DocumentSetCreate,
    Keyword,
    KeywordCreate,
    MessageIn,
    MessageOut,
    PagedDocumentOut,
)
from app.core import llm, ac


def create_document_set(session: Session, docset_create: DocumentSetCreate):
    db_docset = DocumentSet.model_validate(docset_create)
    session.add(db_docset)
    session.commit()
    session.refresh(db_docset)

    db_docset.get_save_dir().mkdir(parents=True, exist_ok=True)
    db_docset.get_documents_dir().mkdir(exist_ok=True)
    db_docset.get_vectorstore_dir().mkdir(exist_ok=True)
    return db_docset


def delete_document_set(session: Session, docset: DocumentSet):
    session.exec(delete(Document).where(Document.document_set_id == docset.id))
    session.delete(docset)
    session.commit()
    # delete files under the path of the document set
    shutil.rmtree(docset.get_save_dir())


def create_document_from_upload(session: Session, file: UploadFile, docset_id: int):
    file = (file.filename, file.file.read())
    return create_document(session, file, docset_id)


def create_document(session: Session, file: tuple[str, bytes], docset_id: int):
    filename, filedata = file
    db_doc = Document(name=filename, document_set_id=docset_id)
    session.add(db_doc)
    session.commit()

    # save document to fs
    db_doc.get_save_path().write_bytes(filedata)
    # split document into pages, create pages and vectorize them
    _save_to_vectorstore(session, db_doc)

    return db_doc


def get_document_page(doc: Document, page: int):
    vectorstore_path: Path = doc.document_set.get_vectorstore_dir()
    id = f"doc{doc.id}_page{page}"

    vectorstore = Chroma(
        persist_directory=str(vectorstore_path),
        embedding_function=llm.embeddings,
    )

    paged_doc: PagedDocument = vectorstore._collection.get(ids=[id])["documents"]
    if len(paged_doc) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fail to find page {page} of document",
        )

    return PagedDocumentOut(content=paged_doc[0], page=page)


def _save_to_vectorstore(session: Session, doc: Document):
    paged_docs: list[PagedDocument] = PyMuPDFLoader(str(doc.get_save_path())).load()

    _save_pages_to_vectorstore(session=session, doc=doc, paged_docs=paged_docs)


def _save_pages_to_vectorstore(
    session: Session,
    doc: Document,
    paged_docs: list[PagedDocument],
):
    doc.page_num = len(paged_docs)
    session.add(doc)
    session.commit()

    ids: list[str] = []
    for no, paged_doc in enumerate(paged_docs):
        ids.append(f"doc{doc.id}_page{no}")
        paged_doc.metadata["doc_id"] = doc.id

    vectorstore_path: Path = doc.document_set.get_vectorstore_dir()
    Chroma.from_documents(
        paged_docs,
        llm.embeddings,
        ids=ids,
        persist_directory=str(vectorstore_path),
    )


def delete_document(session: Session, doc: Document):
    # remove pages from vector store
    _remove_from_vectorstore(doc=doc)

    session.delete(doc)
    session.commit()
    # delete document from fs
    doc.get_save_path().unlink()


def _remove_from_vectorstore(doc: Document):
    vectorstore_path: Path = doc.document_set.get_vectorstore_dir()
    ids = [f"doc{doc.id}_page{no}" for no in range(doc.page_num)]

    vectorstore = Chroma(
        persist_directory=str(vectorstore_path),
        embedding_function=llm.embeddings,
    )
    vectorstore._collection.delete(ids=ids)


def create_chat(session: Session, chat_create: ChatCreate):
    db_chat = Chat.model_validate(chat_create)
    session.add(db_chat)
    session.commit()
    session.refresh(db_chat)
    return db_chat


def list_chats(session: Session):
    return session.exec(select(Chat)).all()


def post_message_in_chat(session: Session, chat: Chat, message: MessageIn):
    content = message.content

    keywords = _get_keywords_in_content(session, content)
    # convert Keywords to dict
    keywords_dict = {keyword.keyword: keyword.prompt for keyword in keywords}

    # invoke the llm chain and return llm's answer
    result = llm.chain.invoke(
        {"input": message.content, "keywords": keywords_dict},
        config={
            "configurable": {
                "session_id": chat.id,
                "vectorstore": (
                    str(chat.document_set.get_vectorstore_dir())
                    if chat.document_set != None
                    else None
                ),
            }
        },
    )

    message_out: BaseMessage = result["answer"]

    return MessageOut(
        role="ai",
        content=message_out.content,
        documents=[
            DocumentOutWithPage.model_validate(doc)
            for doc in message_out.additional_kwargs.get("documents", [])
        ],
    )


def _get_keywords_in_content(session: Session, content: str):
    if len(ac.automaton) == 0:
        return list[Keyword]()
    keyword_ids: set[int] = set()
    for _, keyword_id in ac.automaton.iter(content):
        keyword_ids.add(keyword_id)

    keywords: list[Keyword] = session.exec(
        select(Keyword).where(col(Keyword.id).in_(keyword_ids))
    ).all()
    return keywords


def delete_chat(session: Session, chat: Chat):
    session.delete(chat)
    session.commit()
    # delete chat history
    _delete_chat_history(chat_id=chat.id)


def _delete_chat_history(chat_id: int):
    history = llm.get_sql_history(chat_id)
    history.clear()


def list_chat_history(chat_id: int):
    history = llm.get_sql_history(chat_id)
    messages: list[BaseMessage] = history.messages
    messages_out: list[MessageOut] = []
    for message in messages:
        messages_out.append(
            MessageOut(
                role=message.type,
                content=message.content,
                documents=[
                    DocumentOutWithPage.model_validate(doc)
                    for doc in message.additional_kwargs.get("documents", [])
                ],
            )
        )

    return messages_out


def get_chat_history(chat_id: int, history_no: int):
    messages = list_chat_history(chat_id)
    if history_no >= len(messages):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fail to find history with no. {history_no}",
        )
    return messages[history_no]


def create_keyword(session: Session, keyword_create: KeywordCreate):
    db_keyword = Keyword.model_validate(keyword_create)
    session.add(db_keyword)
    session.commit()
    session.refresh(db_keyword)

    ac.automaton.add_word(db_keyword.keyword, db_keyword.id)
    ac.automaton.make_automaton()

    return db_keyword


def delete_keyword(session: Session, keyword: Keyword):
    ac.automaton.remove_word(keyword.keyword)
    ac.automaton.make_automaton()

    session.delete(keyword)
    session.commit()


def list_keywords(session: Session):
    return session.exec(select(Keyword)).all()
