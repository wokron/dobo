from importlib import import_module
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda, RunnableConfig
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import Chroma
from langchain_community.chat_message_histories import SQLChatMessageHistory

from app.core.config import settings


def _get_embeddings():
    embeddings_cls = getattr(
        import_module("langchain_community.embeddings"), settings.embeddings.type
    )
    return embeddings_cls(**settings.embeddings.config)


embeddings = _get_embeddings()


def _get_model():
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
            "user",
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
    ]
)


def _create_chain(model):
    def select_retriever(text: str, config: RunnableConfig):
        vectorstore = Chroma(
            persist_directory=config["configurable"]["vectorstore"],
            embedding_function=embeddings,
        )
        return vectorstore.as_retriever()

    retriever = RunnableLambda(select_retriever)
    retriever_chain = create_history_aware_retriever(model, retriever, RETRIEVER_PROMPT)
    document_chain = create_stuff_documents_chain(model, ANSWER_PROMPT)
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


chain = _create_chain(model)
