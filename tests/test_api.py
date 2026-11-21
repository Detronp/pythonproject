import pytest

from app import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app({"DATABASE": str(tmp_path / "test.db"), "TESTING": True})
    return app.test_client()


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}


def test_index(client):
    assert client.get("/").get_json()["service"] == "task-api"


def test_crud_flow(client):
    assert client.get("/tasks").get_json() == []

    r = client.post("/tasks", json={"title": "Write Dockerfile"})
    assert r.status_code == 201
    task = r.get_json()
    assert task["title"] == "Write Dockerfile" and task["done"] is False

    r = client.patch(f"/tasks/{task['id']}", json={"done": True})
    assert r.get_json()["done"] is True

    assert len(client.get("/tasks").get_json()) == 1
    assert client.delete(f"/tasks/{task['id']}").status_code == 204
    assert client.get(f"/tasks/{task['id']}").status_code == 404


def test_validation(client):
    assert client.post("/tasks", json={}).status_code == 400
    assert client.post("/tasks", json={"title": "   "}).status_code == 400


def test_missing_task(client):
    assert client.patch("/tasks/999", json={"done": True}).status_code == 404
    assert client.delete("/tasks/999").status_code == 404
