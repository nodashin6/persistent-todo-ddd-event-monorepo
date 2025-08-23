from __future__ import annotations
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from .database import SessionLocal
from .repositories import SQLAlchemyTodoRepository


class AbstractUnitOfWork(ABC):
    todos: SQLAlchemyTodoRepository

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    def __enter__(self):
        self.session: Session = self.session_factory()
        self.todos = SQLAlchemyTodoRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
