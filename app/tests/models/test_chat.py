from sqlmodel import Session

from app.models import Chat
from app.tests.utils.chat import create_random_chat
from app.tests.utils.document_set import create_random_document_set
from app.tests.utils.utils import get_random_lower_string


def test_create_chat(session: Session):
    docset = create_random_document_set(session)
    db_chat = Chat(name=get_random_lower_string(), document_set=docset)
    session.add(db_chat)
    session.commit()
    assert db_chat.id != None


def test_delete_chat(session: Session):
    db_chat = create_random_chat(session)

    docset = db_chat.document_set
    assert len(docset.chats) == 1
    assert docset.chats[0].model_dump() == db_chat.model_dump()

    session.delete(db_chat)
    session.commit()

    session.flush(docset)
    assert len(docset.chats) == 0


def test_get_chat(session: Session):
    db_chat = create_random_chat(session)

    chat_id = db_chat.id
    db_chat2 = session.get(Chat, chat_id)
    assert db_chat.model_dump() == db_chat2.model_dump()
