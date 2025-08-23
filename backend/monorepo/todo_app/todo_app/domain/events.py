from dataclasses import dataclass
import datetime

from .common.events import DomainEvent

@dataclass(frozen=True, kw_only=True)
class TodoCreated(DomainEvent):
    todo_id: int
    task: str

@dataclass(frozen=True, kw_only=True)
class TodoCompleted(DomainEvent):
    todo_id: int


@dataclass(frozen=True, kw_only=True)
class UserCreated(DomainEvent):
    user_id: int
    username: str
