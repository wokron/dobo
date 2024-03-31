from pathlib import Path
import shutil
from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session, delete

from app.core.config import DEFAULT_DATABASE_FILE, DEFAULT_MEMORY_FILE, settings
from app.models import Chat, Document, DocumentSet
from app.core.db import engine
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def session():
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
def wrapper_session():
    yield
    Path(DEFAULT_DATABASE_FILE).unlink(missing_ok=True)
    Path(DEFAULT_MEMORY_FILE).unlink(missing_ok=True)
    shutil.rmtree(settings.data_dir, ignore_errors=True)
    session.commit()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
