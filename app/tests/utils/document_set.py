from sqlmodel import Session

from app import crud
from app.models import DocumentSetCreate
from app.tests.utils.utils import get_random_lower_string


def create_random_document_set(session: Session):
    name = get_random_lower_string()
    db_docset = crud.create_document_set(
        session=session, docset_create=DocumentSetCreate(name=name)
    )
    return db_docset
