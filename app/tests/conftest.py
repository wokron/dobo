from pathlib import Path
import shutil
import pytest
from sqlmodel import Session, delete

from app.core.config import settings
from app.models import Chat, Document, DocumentSet
from app.core.db import engine


@pytest.fixture(scope="session", autouse=True)
def session():
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
def wrapper_session():
    yield
    Path("database.db").unlink(missing_ok=True)
    shutil.rmtree(settings.DATA_DIR, ignore_errors=True)


@pytest.fixture(scope="module", autouse=True)
def wrapper_module(session: Session):
    yield
    session.exec(delete(DocumentSet))
    session.exec(delete(Document))
    session.exec(delete(Chat))
    session.commit()
    Path("memory.db").unlink(missing_ok=True)


@pytest.fixture(scope="module", autouse=True)
def docset(session: Session):
    db_docset = DocumentSet(name="docset")
    session.add(db_docset)
    session.commit()
    return db_docset


@pytest.fixture(scope="module", autouse=True)
def doc(session: Session, docset: DocumentSet):
    db_doc = Document(name="doc", document_set=docset)
    session.add(db_doc)
    session.commit()
    return db_doc
