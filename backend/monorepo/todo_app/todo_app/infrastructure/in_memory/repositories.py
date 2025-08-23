import copy
from typing import List, Optional

from ...domain.models import User, Todo, SubTask, Category
from ...domain.repositories import UserRepository, TodoRepository, CategoryRepository


class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._users = {}
        self._next_id = 1

    def add(self, user: User) -> User:
        if self.get_by_username(user.username):
            raise ValueError("User with this username already exists")

        new_user = copy.deepcopy(user)
        new_user.id = self._next_id
        self._users[new_user.id] = new_user
        self._next_id += 1
        return copy.deepcopy(new_user)

    def get_by_username(self, username: str) -> Optional[User]:
        for user in self._users.values():
            if user.username == username:
                return copy.deepcopy(user)
        return None

    def get(self, user_id: int) -> Optional[User]:
        user = self._users.get(user_id)
        return copy.deepcopy(user) if user else None


class InMemoryCategoryRepository(CategoryRepository):
    def __init__(self):
        self._categories = {}
        self._next_id = 1

    def add(self, category: Category) -> Category:
        new_category = copy.deepcopy(category)
        new_category.id = self._next_id
        self._categories[new_category.id] = new_category
        self._next_id += 1
        return copy.deepcopy(new_category)

    def get(self, category_id: int, user_id: int) -> Optional[Category]:
        category = self._categories.get(category_id)
        if category and category.user_id == user_id:
            return copy.deepcopy(category)
        return None

    def list_by_user(self, user_id: int) -> List[Category]:
        return [
            copy.deepcopy(cat)
            for cat in self._categories.values()
            if cat.user_id == user_id
        ]

    def update(self, category: Category) -> Optional[Category]:
        if category.id not in self._categories or self._categories[category.id].user_id != category.user_id:
            return None
        self._categories[category.id] = copy.deepcopy(category)
        return category

    def delete(self, category_id: int, user_id: int) -> bool:
        category = self._categories.get(category_id)
        if category and category.user_id == user_id:
            del self._categories[category_id]
            return True
        return False


class InMemoryTodoRepository(TodoRepository):
    def __init__(self):
        self._todos = {}
        self._next_id = 1
        self._next_subtask_id = 1

    def add(self, todo: Todo) -> Todo:
        new_todo = copy.deepcopy(todo)
        new_todo.id = self._next_id
        self._todos[new_todo.id] = new_todo
        self._next_id += 1
        return copy.deepcopy(new_todo)

    def get(self, todo_id: int, user_id: int) -> Optional[Todo]:
        todo = self._todos.get(todo_id)
        if todo and todo.user_id == user_id:
            return copy.deepcopy(todo)
        return None

    def list(self, user_id: int) -> List[Todo]:
        user_todos = [
            copy.deepcopy(todo)
            for todo in self._todos.values()
            if todo.user_id == user_id
        ]
        return user_todos

    def update(self, todo: Todo) -> Optional[Todo]:
        if todo.id not in self._todos or self._todos[todo.id].user_id != todo.user_id:
            return None

        # Assign IDs to new subtasks
        for subtask in todo.subtasks:
            if subtask.id is None:
                subtask.id = self._next_subtask_id
                self._next_subtask_id += 1

        self._todos[todo.id] = copy.deepcopy(todo)
        return todo

    def delete(self, todo_id: int, user_id: int) -> bool:
        todo = self._todos.get(todo_id)
        if todo and todo.user_id == user_id:
            del self._todos[todo_id]
            return True
        return False
