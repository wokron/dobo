from sqlmodel import Session

from app import crud
from app.models import ChatCreate
from app.tests.utils.document_set import create_random_document_set
from app.tests.utils.utils import get_random_lower_string


def create_random_chat(session: Session):
    docset = create_random_document_set(session)
    name = get_random_lower_string()
    db_chat = crud.create_chat(
        session=session,
        chat_create=ChatCreate(name=name, document_set_id=docset.id),
    )
    return db_chat
