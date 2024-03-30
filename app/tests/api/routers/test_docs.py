from fastapi.testclient import TestClient
from sqlmodel import Session

from app.tests.utils.document import create_random_document


def test_download_document(client: TestClient, session: Session):
    doc = create_random_document(session)

    response = client.get(f"/docs/{doc.id}")
    assert response.status_code == 200

    data = response.read()
    assert len(data) != 0


def test_delete_document(client: TestClient, session: Session):
    doc = create_random_document(session)

    response = client.delete(f"/docs/{doc.id}")
    assert response.status_code == 200
