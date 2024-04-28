from importlib import import_module
import json
from operator import itemgetter
from typing import Any

from fastapi import HTTPException, status
import httpx
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda, RunnableConfig
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import Chroma
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_community.chat_message_histories.sql import (
    BaseMessageConverter,
    messages_from_dict,
    message_to_dict,
)
from langchain.globals import set_debug, set_verbose
from langchain_core.language_models import BaseChatModel
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    ChatMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.runnables import RunnableBranch, RunnableParallel, RunnablePick
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, BaseMessage
from sqlalchemy import JSON, Column, Integer, Text
from sqlalchemy.orm import declarative_base
from sqlmodel import Field, SQLModel, Session


from app.core.config import settings
from app.core.db import engine
from app.models import Document, DocumentOutWithPage

set_verbose(settings.chain.verbose)
set_debug(settings.chain.debug)


def _get_embeddings():
    embeddings_cls = getattr(
        import_module("langchain_community.embeddings"), settings.embeddings.type
    )
    return embeddings_cls(**settings.embeddings.config)


embeddings = _get_embeddings()


class CustomChatModel(BaseChatModel):
    request_url: str
    timeout: float = 120.0

    def _generate(
        self,
        messages: list[BaseMessage],
        **kwargs: Any,
    ) -> ChatResult:

        # Replace this with actual logic to generate a response from a list
        # of messages.
        messages_texts: list[str] = []

        for message in messages:
            messages_texts.append(_convert_message_to_text(message))

        messages_text = "\n".join(messages_texts + ["ai:"])
        
        try:
            response = httpx.post(
                self.request_url,
                json={"content": messages_text},
                timeout=self.timeout,
            )
        except httpx.TimeoutException:
            raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Request LLM api timeout")
        if response.status_code != 200:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Fail to request LLM api")

        content = response.json()

        response_message = AIMessage(content=content["result"])

        generation = ChatGeneration(message=response_message)
        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        return "custom-chat-model"

    @property
    def _identifying_params(self) -> dict[str, Any]:
        return {"model_name": "custom-chat-model"}


def _convert_message_to_text(message: BaseMessage):
    if isinstance(message, ChatMessage):
        return f"{message.role}: {message.content}"
    elif isinstance(message, HumanMessage):
        return f"user: {message.content}"
    elif isinstance(message, AIMessage):
        return f"assistant: {message.content}"
    elif isinstance(message, SystemMessage):
        return f"system: {message.content}"
    else:
        raise TypeError(f"Got unknown type {message}")


def _get_model():
    if settings.llm.type == "CustomChatModel":
        model_cls = CustomChatModel
    else:
        model_cls = getattr(
            import_module("langchain_community.chat_models"), settings.llm.type
        )
    model = model_cls(**settings.llm.config)
    return model


model = _get_model()


RETRIEVER_PROMPT = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        (
            "system",
            "根据上述对话，生成要查找的搜索查询，以获取与对话相关的信息",
        ),
    ]
)


ANSWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "根据系统提供的以下上下文回答用户的问题：\n\n{context}",
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        ("system", "{keywords}"),
    ]
)


class MessageWithCiteConverter(BaseMessageConverter):

    def __init__(self):
        class Message(declarative_base()):  # type: ignore[valid-type, misc]
            __tablename__ = "message_store"
            id = Column(Integer, primary_key=True)
            session_id = Column(Text)
            message = Column(Text)
            additional_kwargs = Column(JSON)

        self.model_class = Message

    def from_sql_model(self, sql_message: Any) -> BaseMessage:
        message = messages_from_dict([json.loads(sql_message.message)])[0]
        message.additional_kwargs = sql_message.additional_kwargs
        return message

    def to_sql_model(self, message: BaseMessage, session_id: str) -> Any:
        return self.model_class(
            session_id=session_id,
            message=json.dumps(message_to_dict(message)),
            additional_kwargs=message.additional_kwargs,
        )

    def get_sql_model_class(self) -> Any:
        return self.model_class


def get_sql_history(session_id: int):
    return SQLChatMessageHistory(
        session_id=session_id,
        connection_string=settings.memory_url,
        custom_message_converter=MessageWithCiteConverter(),
    )


def _create_chain(model):
    def _select_retriever(text: str, config: RunnableConfig):
        if config["configurable"]["vectorstore"] == None:
            return ""

        vectorstore = Chroma(
            persist_directory=config["configurable"]["vectorstore"],
            embedding_function=embeddings,
        )
        return vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "score_threshold": settings.vectorstore.score_threshold,
                "k": settings.vectorstore.top_k,
            },
        )

    def _create_history_aware_retriever(llm, retriever, prompt):

        def _prepend_origin_input(data):
            return data["input"] + " " + data["output"].content

        retrieve_documents = RunnableBranch(
            (
                # Both empty string and empty list evaluate to False
                lambda x: not x.get("chat_history", False),
                # If no chat history, then we just pass input to retriever
                (lambda x: x["input"]) | retriever,
            ),
            # If chat history, then we pass inputs to LLM chain, then to retriever
            RunnableParallel(input=RunnablePick("input"), output=prompt | llm)
            | RunnableLambda(_prepend_origin_input)
            | StrOutputParser()
            | retriever,
        ).with_config(run_name="chat_retriever_chain")
        return retrieve_documents

    retriever = RunnableLambda(_select_retriever)

    if settings.vectorstore.history_aware:
        retriever_chain = _create_history_aware_retriever(
            model, retriever, RETRIEVER_PROMPT
        )
    else:
        retriever_chain = (lambda x: x["input"]) | retriever

    document_chain = create_stuff_documents_chain(model, ANSWER_PROMPT)
    retrieval_chain = create_retrieval_chain(retriever_chain, document_chain)

    def _format_keywords(data):
        keywords: dict[str, str] = data["keywords"]
        if len(keywords) == 0:
            return "无补充信息"
        else:
            return "\n\n".join(
                [f"**{keyword}**: {prompt}" for keyword, prompt in keywords.items()]
            )

    chat_chain = (
        {
            "keywords": RunnableLambda(_format_keywords),
            "input": itemgetter("input"),
            "chat_history": itemgetter("chat_history"),
        }
        | retrieval_chain
        | RunnableLambda(_attach_document_page)
    )

    chain_with_chat_history = RunnableWithMessageHistory(
        chat_chain,
        lambda session_id: get_sql_history(session_id),
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    return chain_with_chat_history


def _attach_document_page(result):
    with Session(engine) as session:
        documents: dict[int, DocumentOutWithPage] = {}
        for doc in result["context"]:
            doc_id = doc.metadata["doc_id"]
            doc_page_no = doc.metadata["page"]
            if doc_id in documents:
                documents[doc_id].pages.append(doc_page_no)
            else:
                db_doc = session.get(Document, doc_id)
                documents[doc_id] = DocumentOutWithPage.model_validate(
                    db_doc, update={"pages": [doc_page_no]}
                )

    result["answer"] = AIMessage(
        content=result["answer"],
        additional_kwargs={"documents": [doc.model_dump() for doc in documents.values()]},
    )

    return result


chain = _create_chain(model)
