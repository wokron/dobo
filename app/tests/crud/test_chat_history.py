from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import MessageIn
from app.tests.utils.chat import create_random_chat


def test_add_chat_history(session: Session):
    chat = create_random_chat(session)
    memory: BaseChatMessageHistory = SQLChatMessageHistory(
        session_id=chat.id,
        connection_string=settings.memory_url,
    )

    assert len(memory.messages) == 0

    memory.add_ai_message("here is ai")
    memory.add_user_message("here is human")

    assert len(memory.messages) == 2

    chat2 = create_random_chat(session)
    memory2: BaseChatMessageHistory = SQLChatMessageHistory(
        session_id=chat2.id,
        connection_string=settings.memory_url,
    )

    assert len(memory2.messages) == 0


def test_add_and_get_chat_history(session: Session):
    chat = create_random_chat(session)

    crud.post_message_in_chat(chat, MessageIn(content="Hello1"))
    crud.post_message_in_chat(chat, MessageIn(content="Hello2"))

    messages = crud.list_chat_history(chat_id=chat.id)
    assert len(messages) == 4
    assert [message.model_dump() for message in messages] == [
        {"role": "human", "content": "Hello1"},
        {"role": "ai", "content": "I don't know"},
        {"role": "human", "content": "Hello2"},
        {"role": "ai", "content": "I don't know"},
    ]


def test_delete_chat_history(session: Session):
    chat = create_random_chat(session)

    crud.post_message_in_chat(chat, MessageIn(content="Hello1"))

    memory: BaseChatMessageHistory = SQLChatMessageHistory(
        session_id=chat.id,
        connection_string=settings.memory_url,
    )

    assert len(memory.messages) == 2

    crud._delete_chat_history(chat_id=chat.id)

    memory: BaseChatMessageHistory = SQLChatMessageHistory(
        session_id=chat.id,
        connection_string=settings.memory_url,
    )

    assert len(memory.messages) == 0
