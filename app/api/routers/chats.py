from fastapi import APIRouter

from app import crud
from app.api.deps import ChatDep, SessionDep
from app.core import llm
from app.models import ChatCreate, ChatOut, MessageIn, MessageOut


router = APIRouter()


@router.post("/", response_model=ChatOut)
def create_chat(session: SessionDep, chat_create: ChatCreate):
    return crud.create_chat(session=session, chat_create=chat_create)


@router.post("/{chat_id}", response_model=MessageOut)
def post_message(chat: ChatDep, message: MessageIn):
    return crud.post_message_in_chat(chat, message)


@router.get("/{chat_id}", response_model=list[MessageOut])
def get_chat_history(chat: ChatDep):
    return crud.list_chat_history(chat_id=chat.id)


@router.delete("/{chat_id}")
def delete_chat(session: SessionDep, chat: ChatDep):
    crud.delete_chat(session, chat)
