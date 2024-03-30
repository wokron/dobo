from sqlmodel import Session, select, delete

from app.models import Chat, DocumentSet


def test_create_chat(session: Session, docset: DocumentSet):
    db_chat = Chat(name="chat1", document_set=docset)
    session.add(db_chat)
    session.commit()
    assert db_chat.id != None


def test_delete_chat(session: Session, docset: DocumentSet):
    db_chat = session.exec(select(Chat).where(Chat.name == "chat1")).one()

    session.flush(docset)
    assert len(docset.chats) == 1
    assert docset.chats[0].model_dump() == db_chat.model_dump()

    session.delete(db_chat)
    session.commit()

    session.flush(docset)
    assert len(docset.chats) == 0


def test_get_chat(session: Session, docset: DocumentSet):
    db_chat = Chat(name="chat2", document_set=docset)
    session.add(db_chat)
    session.commit()

    chat_id = db_chat.id
    db_chat2 = session.get(Chat, chat_id)
    assert db_chat.model_dump() == db_chat2.model_dump()
