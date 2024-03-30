from fastapi import APIRouter

from app import crud
from app.api.deps import ChainDep, ChatDep, SessionDep
from app.models import ChatCreate, ChatOut, MessageIn, MessageOut


router = APIRouter()


@router.post("/", response_model=ChatOut)
def create_chat(session: SessionDep, chat_create: ChatCreate):
    return crud.create_chat(session=session, chat_create=chat_create)


@router.post("/{chat_id}", response_model=MessageOut)
def post_message(chain: ChainDep, chat: ChatDep, message: MessageIn):
    # invoke the llm chain and return llm's answer
    result = chain.invoke(
        {"input": message.content},
        config={
            "configurable": {
                "session_id": chat.id,
                "vectorstore": str(chat.document_set.get_vector_store_path()),
            }
        },
    )
    return MessageOut(role="ai", content=result["answer"])


@router.get("/{chat_id}", response_model=list[MessageOut])
def get_chat_history(chat: ChatDep):
    return crud.get_chat_history(chat_id=chat.id)


@router.delete("/{chat_id}")
def delete_chat(session: SessionDep, chat: ChatDep):
    session.delete(chat)
    session.commit()
    # delete chat history
    crud.delete_chat_history(chat_id=chat.id)
