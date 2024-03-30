from fastapi.testclient import TestClient
from sqlmodel import Session

from app.tests.utils.document import create_random_document
from app.tests.utils.document_set import create_random_document_set
from app.tests.utils.utils import get_random_lower_string, get_random_pdf


def test_create_document_set(client: TestClient):
    name = get_random_lower_string()
    response = client.post("/docsets", json={"name": name})
    assert response.status_code == 200
    content = response.json()
    assert "id" in content
    assert content["name"] == name


def test_delete_document_set(client: TestClient, session: Session):
    docset = create_random_document_set(session)
    response = client.delete(f"/docsets/{docset.id}")
    assert response.status_code == 200


def test_list_document_sets(client: TestClient, session: Session):
    docsets = [create_random_document_set(session) for _ in range(5)]
    response = client.get("/docsets")
    content = response.json()

    ids: set[int] = {docset.id for docset in docsets}
    ids_in_content: set[int] = {content_elm["id"] for content_elm in content}
    assert response.status_code == 200
    assert ids.issubset(ids_in_content)


def test_upload_document(client: TestClient, session: Session):
    docset = create_random_document_set(session)
    files = [get_random_pdf()]
    response = client.post(
        f"/docsets/{docset.id}/docs",
        files=[("files", file) for file in files],
    )
    assert response.status_code == 200
    content = response.json()

    assert len(content) == len(files)
    data = [{"name": file[0], "document_set_id": docset.id} for file in files]
    for content_elm, data_elm in zip(content, data):
        assert "id" in content_elm
        assert content_elm["name"] == data_elm["name"]
        assert content_elm["document_set_id"] == data_elm["document_set_id"]


def test_list_documents(client: TestClient, session: Session):
    doc = create_random_document(session)
    response = client.get(f"/docsets/{doc.document_set.id}/docs")
    assert response.status_code == 200
    content = response.json()

    assert len(content) == 1
    assert doc.model_dump(include=["id", "name", "document_set_id"]) == content[0]
