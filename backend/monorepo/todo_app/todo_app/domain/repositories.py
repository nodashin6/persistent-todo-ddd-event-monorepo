from abc import ABC, abstractmethod
from typing import List, Optional
from .models import Todo


class TodoRepository(ABC):
    @abstractmethod
    def add(self, todo: Todo):
        raise NotImplementedError

    @abstractmethod
    def get(self, todo_id: int) -> Optional[Todo]:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> List[Todo]:
        raise NotImplementedError

    @abstractmethod
    def update(self, todo: Todo):
        raise NotImplementedError
