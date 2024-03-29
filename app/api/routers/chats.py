from fastapi import APIRouter

from app import crud
from app.api.deps import ChatDep, SessionDep
from app.models import ChatCreate, ChatOut, MessageIn, MessageOut


router = APIRouter()


@router.post("/", response_model=ChatOut)
def create_chat(session: SessionDep, chat_create: ChatCreate):
    return crud.create_chat(session=session, chat_create=chat_create)


@router.post("/{chat_id}")
def post_message(session: SessionDep, chat: ChatDep, message: MessageIn):
    # TODO: load vectorstore and memory, invoke llm agent and return the agent response
    pass


@router.get("/{chat_id}", response_model=list[MessageOut])
def get_chat_history():
    pass


@router.delete("/{chat_id}")
def delete_chat(session: SessionDep, chat: ChatDep):
    session.delete(chat)
    session.commit()
    # TODO: delete chat memories
