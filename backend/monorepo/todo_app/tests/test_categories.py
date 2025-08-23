import pytest
from fastapi.testclient import TestClient
from todo_app.main import app
from todo_app.presentation.dependencies import get_uow
from todo_app.infrastructure.in_memory.unit_of_work import InMemoryUnitOfWork
from todo_app.domain.models import User, Todo, Category

# In-memory UoW for testing
@pytest.fixture(scope="function")
def uow():
    return InMemoryUnitOfWork()

# Override the dependency with the in-memory version for all tests
@pytest.fixture(autouse=True)
def override_uow_dependency(uow: InMemoryUnitOfWork):
    app.dependency_overrides[get_uow] = lambda: uow
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_user_factory(client: TestClient):
    """
    A factory to create multiple users for testing authorization.
    """
    created_users = []

    def _create_user(username, password):
        response = client.post(
            "/users/", json={"username": username, "password": password}
        )
        assert response.status_code == 201
        user_data = response.json()

        login_response = client.post(
            "/token", data={"username": username, "password": password}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        user_info = {"user": user_data, "headers": headers}
        created_users.append(user_info)
        return user_info

    yield _create_user

    # Clean up if needed, though in-memory UoW resets each test
    created_users.clear()


def test_category_crud(client: TestClient, test_user_factory):
    user1 = test_user_factory("user1", "pass1")
    headers1 = user1["headers"]

    # Create a category
    response = client.post("/categories/", json={"name": "Work"}, headers=headers1)
    assert response.status_code == 201
    category_data = response.json()
    assert category_data["name"] == "Work"
    assert "id" in category_data
    category_id = category_data["id"]

    # Read categories
    response = client.get("/categories/", headers=headers1)
    assert response.status_code == 200
    categories = response.json()
    assert len(categories) == 1
    assert categories[0]["name"] == "Work"

    # Update the category
    response = client.put(
        f"/categories/{category_id}", json={"name": "Personal"}, headers=headers1
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Personal"

    # Delete the category
    response = client.delete(f"/categories/{category_id}", headers=headers1)
    assert response.status_code == 204

    # Verify deletion
    response = client.get("/categories/", headers=headers1)
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_category_authorization(client: TestClient, test_user_factory):
    user1 = test_user_factory("user1", "pass1")
    user2 = test_user_factory("user2", "pass2")
    headers1 = user1["headers"]
    headers2 = user2["headers"]

    # User 1 creates a category
    response = client.post("/categories/", json={"name": "User1's Cat"}, headers=headers1)
    assert response.status_code == 201
    category_id = response.json()["id"]

    # User 2 cannot see User 1's category
    response = client.get("/categories/", headers=headers2)
    assert response.status_code == 200
    assert len(response.json()) == 0

    # User 2 cannot update User 1's category
    response = client.put(
        f"/categories/{category_id}", json={"name": "Hacked"}, headers=headers2
    )
    assert response.status_code == 404

    # User 2 cannot delete User 1's category
    response = client.delete(f"/categories/{category_id}", headers=headers2)
    assert response.status_code == 404


def test_assign_and_remove_category(client: TestClient, test_user_factory, uow: InMemoryUnitOfWork):
    user = test_user_factory("user1", "pass1")
    headers = user["headers"]
    user_id = user["user"]["id"]

    # Create a Todo
    todo = uow.todos.add(Todo.create(task="Categorized Todo", user_id=user_id))
    uow.commit()
    todo_id = todo.id

    # Create a Category
    category = uow.categories.add(Category(id=None, user_id=user_id, name="Urgent"))
    uow.commit()
    category_id = category.id

    # Assign category to todo
    response = client.post(
        f"/todos/{todo_id}/categories/{category_id}", headers=headers
    )
    assert response.status_code == 200
    todo_data = response.json()
    assert len(todo_data["categories"]) == 1
    assert todo_data["categories"][0]["name"] == "Urgent"

    # Remove category from todo
    response = client.delete(
        f"/todos/{todo_id}/categories/{category_id}", headers=headers
    )
    assert response.status_code == 200
    todo_data_after_remove = response.json()
    assert len(todo_data_after_remove["categories"]) == 0
