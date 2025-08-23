import datetime
from typing import Optional

from .common.entities import AggregateRoot
from .events import TodoCreated, TodoCompleted


class Todo(AggregateRoot[int, TodoCreated | TodoCompleted]):
    def __init__(
        self,
        id: Optional[int],
        task: str,
        is_completed: bool,
        created_at: datetime.datetime,
        updated_at: datetime.datetime,
    ):
        super().__init__(id)
        self.task = task
        self.is_completed = is_completed
        self.created_at = created_at
        self.updated_at = updated_at

    def complete(self):
        if not self.is_completed:
            self.is_completed = True
            self.updated_at = datetime.datetime.now(datetime.timezone.utc)
            # The ID should be set by the repository after creation
            if self.id is not None:
                self._add_domain_event(TodoCompleted(todo_id=self.id))

    @staticmethod
    def create(task: str) -> "Todo":
        now = datetime.datetime.now(datetime.timezone.utc)
        todo = Todo(
            id=None,  # The ID will be assigned by the database
            task=task,
            is_completed=False,
            created_at=now,
            updated_at=now,
        )
        # We can't add a TodoCreated event here yet, because the ID is not assigned.
        # This highlights a limitation of the current design.
        # The event should be created and dispatched by the application service
        # or repository after the ID is known.
        return todo
