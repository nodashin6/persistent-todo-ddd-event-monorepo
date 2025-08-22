from fastapi.testclient import TestClient
from todo_app.main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_read_todos():
    response = client.get("/todos/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_todo():
    response = client.post("/todos/", json={"task": "Test todo"})
    assert response.status_code == 200
    assert response.json() == {"message": "Todo creation request received"}
