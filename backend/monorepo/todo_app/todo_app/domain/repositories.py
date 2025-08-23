from abc import ABC, abstractmethod
from typing import List, Optional
from .models import Todo, User, Category


class CategoryRepository(ABC):
    @abstractmethod
    def add(self, category: Category) -> Category:
        raise NotImplementedError

    @abstractmethod
    def get(self, category_id: int, user_id: int) -> Optional[Category]:
        raise NotImplementedError

    @abstractmethod
    def list_by_user(self, user_id: int) -> List[Category]:
        raise NotImplementedError

    @abstractmethod
    def update(self, category: Category) -> Optional[Category]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, category_id: int, user_id: int) -> bool:
        raise NotImplementedError


class UserRepository(ABC):
    @abstractmethod
    def add(self, user: User):
        raise NotImplementedError

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        raise NotImplementedError


class TodoRepository(ABC):
    @abstractmethod
    def add(self, todo: Todo):
        raise NotImplementedError

    @abstractmethod
    def get(self, todo_id: int, user_id: int) -> Optional[Todo]:
        raise NotImplementedError

    @abstractmethod
    def list(self, user_id: int) -> List[Todo]:
        raise NotImplementedError

    @abstractmethod
    def update(self, todo: Todo):
        raise NotImplementedError

    @abstractmethod
    def delete(self, todo_id: int, user_id: int):
        raise NotImplementedError
