from fastapi import APIRouter

from app import crud
from app.api.deps import ChatCreateDep, ChatDep, SessionDep
from app.models import ChatOut, ChatResponse, MessageIn, MessageOut


router = APIRouter()


@router.post("/", response_model=ChatOut)
def create_chat(session: SessionDep, chat_create: ChatCreateDep):
    return crud.create_chat(session=session, chat_create=chat_create)


@router.get("/", response_model=list[ChatOut])
def list_chats(session: SessionDep):
    return crud.list_chats(session)


@router.post("/{chat_id}", response_model=ChatResponse)
def post_message(session: SessionDep, chat: ChatDep, message: MessageIn):
    return crud.post_message_in_chat(session, chat, message)


@router.get("/{chat_id}/history", response_model=list[MessageOut])
def list_chat_history(chat: ChatDep):
    return crud.list_chat_history(chat_id=chat.id)


@router.get("/{chat_id}/history/{history_no}", response_model=MessageOut)
def get_chat_history(chat: ChatDep, history_no: int):
    return crud.get_chat_history(chat_id=chat.id, history_no=history_no)


@router.delete("/{chat_id}")
def delete_chat(session: SessionDep, chat: ChatDep):
    crud.delete_chat(session, chat)
