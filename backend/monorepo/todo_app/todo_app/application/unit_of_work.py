from __future__ import annotations
from abc import ABC, abstractmethod
from ..domain import repositories as domain_repos
from . import message_queue


class AbstractUnitOfWork(ABC):
    todos: domain_repos.TodoRepository
    users: domain_repos.UserRepository
    categories: domain_repos.CategoryRepository
    mq: message_queue.MessageQueue

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        if exc_type:
            self.rollback()
        else:
            self.commit()

    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError
