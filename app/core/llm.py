from importlib import import_module
from operator import itemgetter

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda, RunnableConfig
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import Chroma
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain.globals import set_debug, set_verbose
from langchain_core.runnables import RunnableBranch, RunnableParallel, RunnablePick
from langchain_core.output_parsers import StrOutputParser

from app.core.config import settings

set_verbose(settings.chain.verbose)
set_debug(settings.chain.debug)


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

    chat_chain = {
        "keywords": RunnableLambda(_format_keywords),
        "input": itemgetter("input"),
        "chat_history": itemgetter("chat_history"),
    } | retrieval_chain

    chain_with_chat_history = RunnableWithMessageHistory(
        chat_chain,
        lambda session_id: SQLChatMessageHistory(
            session_id=session_id, connection_string=settings.memory_url
        ),
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    return chain_with_chat_history


chain = _create_chain(model)
