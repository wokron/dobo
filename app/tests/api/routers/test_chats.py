from fastapi.testclient import TestClient
from sqlmodel import Session

from app.tests.utils.chat import create_random_chat
from app.tests.utils.document_set import create_random_document_set
from app.tests.utils.utils import get_random_lower_string


def test_create_chat(client: TestClient, session: Session):
    docset = create_random_document_set(session)
    name = get_random_lower_string()
    response = client.post(
        "/chats",
        json={"name": name, "document_set_id": docset.id},
    )
    assert response.status_code == 200

    data = {"name": name, "document_set_id": docset.id}
    content = response.json()
    assert "id" in content
    assert content["name"] == data["name"]
    assert content["document_set_id"] == data["document_set_id"]


def test_post_message(client: TestClient, session: Session):
    chat = create_random_chat(session)
    response = client.post(f"/chats/{chat.id}", json={"content": "Hello"})
    assert response.status_code == 200

    data = {"role": "ai", "content": "I don't know"}
    content = response.json()
    assert content == data


def test_get_chat_history(client: TestClient, session: Session):
    chat = create_random_chat(session)
    response = client.post(f"/chats/{chat.id}", json={"content": "Hello1"})
    assert response.status_code == 200

    response = client.post(f"/chats/{chat.id}", json={"content": "Hello2"})
    assert response.status_code == 200

    response = client.get(f"/chats/{chat.id}")
    assert response.status_code == 200

    data = [
        {"role": "human", "content": "Hello1"},
        {"role": "ai", "content": "I don't know"},
        {"role": "human", "content": "Hello2"},
        {"role": "ai", "content": "I don't know"},
    ]
    content = response.json()
    assert len(content) == 4
    assert content == data


def test_delete_chat(client: TestClient, session: Session):
    chat = create_random_chat(session)
    response = client.delete(f"/chats/{chat.id}")
    assert response.status_code == 200
