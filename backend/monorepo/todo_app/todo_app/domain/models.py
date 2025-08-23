import datetime
from typing import Optional, List

from .common.entities import AggregateRoot
from .events import TodoCreated, TodoCompleted, UserCreated
# NOTE: This creates a dependency from domain to application, which is not ideal.
# A better approach would be to use a domain service for password hashing.
from ..application import security


class SubTask:
    def __init__(
        self,
        id: Optional[int],
        todo_id: int,
        task: str,
        is_completed: bool,
    ):
        self.id = id
        self.todo_id = todo_id
        self.task = task
        self.is_completed = is_completed

    def complete(self):
        self.is_completed = True

    def uncomplete(self):
        self.is_completed = False


class Category(AggregateRoot[int, None]): # No events for now
    def __init__(
        self,
        id: Optional[int],
        user_id: int,
        name: str,
    ):
        super().__init__(id)
        self.user_id = user_id
        self.name = name


class User(AggregateRoot[int, UserCreated]):
    def __init__(
        self,
        id: Optional[int],
        username: str,
        hashed_password: str,
    ):
        super().__init__(id)
        self.username = username
        self.hashed_password = hashed_password

    @staticmethod
    def create(username: str, plain_password: str) -> "User":
        hashed_password = security.get_password_hash(plain_password)
        user = User(
            id=None,
            username=username,
            hashed_password=hashed_password,
        )
        # Event will be dispatched by the repository after ID is assigned
        return user

    def verify_password(self, plain_password: str) -> bool:
        return security.verify_password(plain_password, self.hashed_password)


class Todo(AggregateRoot[int, TodoCreated | TodoCompleted]):
    def __init__(
        self,
        id: Optional[int],
        user_id: int,
        task: str,
        is_completed: bool,
        created_at: datetime.datetime,
        updated_at: datetime.datetime,
        subtasks: List[SubTask] | None = None,
        categories: List[Category] | None = None,
    ):
        super().__init__(id)
        self.user_id = user_id
        self.task = task
        self.is_completed = is_completed
        self.created_at = created_at
        self.updated_at = updated_at
        self.subtasks = subtasks or []
        self.categories = categories or []

    def add_subtask(self, task: str) -> SubTask:
        if self.id is None:
            raise ValueError("Cannot add subtask to a Todo without an ID")
        subtask = SubTask(id=None, todo_id=self.id, task=task, is_completed=False)
        self.subtasks.append(subtask)
        self.updated_at = datetime.datetime.now(datetime.timezone.utc)
        return subtask

    def assign_category(self, category: Category):
        if category not in self.categories:
            self.categories.append(category)
            self.updated_at = datetime.datetime.now(datetime.timezone.utc)

    def remove_category(self, category_id: int):
        self.categories = [cat for cat in self.categories if cat.id != category_id]
        self.updated_at = datetime.datetime.now(datetime.timezone.utc)

    def complete(self):
        if not self.is_completed:
            self.is_completed = True
            self.updated_at = datetime.datetime.now(datetime.timezone.utc)
            # The ID should be set by the repository after creation
            if self.id is not None:
                self._add_domain_event(TodoCompleted(todo_id=self.id))

    def uncomplete(self):
        if self.is_completed:
            self.is_completed = False
            self.updated_at = datetime.datetime.now(datetime.timezone.utc)
            # We could add a TodoUncompleted event here if needed

    @staticmethod
    def create(task: str, user_id: int) -> "Todo":
        now = datetime.datetime.now(datetime.timezone.utc)
        todo = Todo(
            id=None,  # The ID will be assigned by the database
            user_id=user_id,
            task=task,
            is_completed=False,
            created_at=now,
            updated_at=now,
            subtasks=[],
            categories=[],
        )
        # We can't add a TodoCreated event here yet, because the ID is not assigned.
        # This highlights a limitation of the current design.
        # The event should be created and dispatched by the application service
        # or repository after the ID is known.
        return todo
