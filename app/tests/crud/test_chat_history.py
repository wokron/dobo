from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

from app import crud
from app.core.config import settings


def test_add_chat_history():
    memory: BaseChatMessageHistory = SQLChatMessageHistory(
        session_id=1,
        connection_string=settings.memory_url,
    )

    memory.add_ai_message("here is ai")
    memory.add_user_message("here is human")

    assert len(memory.messages) == 2


def test_load_chat_history():
    memory: BaseChatMessageHistory = SQLChatMessageHistory(
        session_id=1,
        connection_string=settings.memory_url,
    )

    assert len(memory.messages) == 2

    memory2: BaseChatMessageHistory = SQLChatMessageHistory(
        session_id=2,
        connection_string=settings.memory_url,
    )

    assert len(memory2.messages) == 0


def test_get_chat_history():
    messages = crud.list_chat_history(chat_id=1)
    assert len(messages) == 2
    assert [message.model_dump() for message in messages] == [
        {"role": "ai", "content": "here is ai"},
        {"role": "human", "content": "here is human"},
    ]


def test_delete_chat_history():
    crud._delete_chat_history(chat_id=1)
    memory: BaseChatMessageHistory = SQLChatMessageHistory(
        session_id=1,
        connection_string=settings.memory_url,
    )

    assert len(memory.messages) == 0
