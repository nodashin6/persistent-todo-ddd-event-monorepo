import datetime
from typing import Optional


class Todo:
    def __init__(
        self,
        id: int,
        task: str,
        is_completed: bool,
        created_at: datetime.datetime,
        updated_at: int,
    ):
        self.id = id
        self.task = task
        self.is_completed = is_completed
        self.created_at = created_at
        self.updated_at = updated_at

    def complete(self):
        self.is_completed = True
        self.updated_at = int(datetime.datetime.now(datetime.timezone.utc).timestamp())

    @staticmethod
    def create(task: str) -> "Todo":
        now = datetime.datetime.now(datetime.timezone.utc)
        return Todo(
            id=None,  # The ID will be assigned by the database
            task=task,
            is_completed=False,
            created_at=now,
            updated_at=int(now.timestamp()),
        )
