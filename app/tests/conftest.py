import pytest
from sqlmodel import Session, delete

from app.models import Chat, Document, DocumentSet, Page
from app.core.db import engine


@pytest.fixture(scope="session", autouse=True)
def session():
    with Session(engine) as session:
        yield session
        session.exec(delete(DocumentSet))
        session.exec(delete(Document))
        session.exec(delete(Page))
        session.exec(delete(Chat))
        session.commit()
