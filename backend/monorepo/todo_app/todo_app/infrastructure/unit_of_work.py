from __future__ import annotations
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import repositories as infra_repos
from ..application.unit_of_work import AbstractUnitOfWork
from ..application import message_queue


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    def __enter__(self):
        self.session: Session = self.session_factory()
        self.todos = infra_repos.SQLAlchemyTodoRepository(self.session)
        self.users = infra_repos.SQLAlchemyUserRepository(self.session)
        self.categories = infra_repos.SQLAlchemyCategoryRepository(self.session)
        self.mq = message_queue.PgmqMessageQueue(self.session)
        return super().__enter__()

    def __exit__(self, exc_type, exc_val, traceback):
        super().__exit__(exc_type, exc_val, traceback)
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
