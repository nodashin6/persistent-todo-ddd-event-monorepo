from dataclasses import dataclass
import datetime

from .common.events import DomainEvent

@dataclass(frozen=True)
class TodoCreated(DomainEvent):
    todo_id: int
    task: str

@dataclass(frozen=True)
class TodoCompleted(DomainEvent):
    todo_id: int
