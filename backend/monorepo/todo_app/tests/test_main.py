import pytest
import json
from fastapi.testclient import TestClient
from todo_app.main import app
from todo_app.presentation.dependencies import get_uow
from todo_app.infrastructure.in_memory.unit_of_work import InMemoryUnitOfWork
from todo_app.domain.models import User, Todo

# In-memory UoW for testing
@pytest.fixture(scope="function")
def uow():
    return InMemoryUnitOfWork()

# Override the dependency with the in-memory version for all tests
@pytest.fixture(autouse=True)
def override_uow_dependency(uow):
    app.dependency_overrides[get_uow] = lambda: uow
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_user(client: TestClient) -> dict:
    """
    Creates a user and returns a dictionary with user data and auth headers.
    """
    response = client.post(
        "/users/", json={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 201
    user_data = response.json()

    # Log in to get token
    login_response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword"},
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    return {"user": user_data, "headers": headers}


def test_register_and_login(client: TestClient):
    # This is implicitly tested by the test_user fixture
    # But we can add an explicit test
    response = client.post(
        "/users/", json={"username": "testuser2", "password": "password123"}
    )
    assert response.status_code == 201
    assert response.json()["username"] == "testuser2"

    login_response = client.post(
        "/token",
        data={"username": "testuser2", "password": "password123"},
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


def test_create_and_read_todo(client: TestClient, test_user: dict):
    headers = test_user["headers"]

    # Create a todo
    create_response = client.post(
        "/todos/",
        json={"task": "Test my new app"},
        headers=headers,
    )
    # The endpoint is async and uses a message queue, so it's 202 Accepted
    assert create_response.status_code == 202

    # Since the worker is not running in tests, we can't directly verify
    # the todo was created. This is a limitation of testing the web app
    # without running the worker.
    # For a full integration test, we would need to run the worker logic.
    # Let's simulate the worker logic for now.

    # Manually run the worker logic
    uow = app.dependency_overrides[get_uow]()
    mq = uow.mq
    msg_tuple = mq.read("todo_queue", 1, 1)
    assert msg_tuple is not None
    msg_id, _, _, _, msg_body = msg_tuple
    msg_data = json.loads(msg_body)

    from todo_app.worker_entrypoint import process_message
    with uow:
        process_message(uow, msg_data)
        uow.commit()

    # Now, read the todos
    read_response = client.get("/todos/", headers=headers)
    assert read_response.status_code == 200
    todos = read_response.json()
    assert len(todos) == 1
    assert todos[0]["task"] == "Test my new app"
    assert todos[0]["is_completed"] is False


def test_unauthorized_access(client: TestClient):
    response = client.get("/todos/")
    assert response.status_code == 401 # Unauthorized


def test_todo_and_subtask_flow(client: TestClient, test_user: dict, uow: InMemoryUnitOfWork):
    headers = test_user["headers"]
    user_id = test_user["user"]["id"]

    # Create a todo
    todo = Todo.create(task="Todo with subtasks", user_id=user_id)
    with uow:
        created_todo = uow.todos.add(todo)
        uow.commit()

    todo_id = created_todo.id

    # Add a subtask
    subtask_response = client.post(
        f"/todos/{todo_id}/subtasks/",
        json={"task": "My first subtask"},
        headers=headers,
    )
    assert subtask_response.status_code == 201
    subtask_data = subtask_response.json()
    assert subtask_data["task"] == "My first subtask"
    assert subtask_data["is_completed"] is False
    subtask_id = subtask_data["id"]

    # Read the todo again to see the subtask
    todo_response = client.get(f"/todos/{todo_id}", headers=headers)
    assert todo_response.status_code == 200
    todo_data = todo_response.json()
    assert len(todo_data["subtasks"]) == 1
    assert todo_data["subtasks"][0]["task"] == "My first subtask"

    # Update the subtask
    update_response = client.put(
        f"/todos/{todo_id}/subtasks/{subtask_id}",
        json={"task": "Updated subtask", "is_completed": True},
        headers=headers,
    )
    assert update_response.status_code == 200
    updated_subtask_data = update_response.json()
    assert updated_subtask_data["task"] == "Updated subtask"
    assert updated_subtask_data["is_completed"] is True

    # Delete the subtask
    delete_response = client.delete(
        f"/todos/{todo_id}/subtasks/{subtask_id}",
        headers=headers,
    )
    assert delete_response.status_code == 204

    # Verify subtask is gone
    todo_response_after_delete = client.get(f"/todos/{todo_id}", headers=headers)
    assert todo_response_after_delete.status_code == 200
    todo_data_after_delete = todo_response_after_delete.json()
    assert len(todo_data_after_delete["subtasks"]) == 0
