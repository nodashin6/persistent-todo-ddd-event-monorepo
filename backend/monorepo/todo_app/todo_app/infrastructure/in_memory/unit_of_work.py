from ...application.unit_of_work import AbstractUnitOfWork
from .repositories import InMemoryTodoRepository, InMemoryUserRepository, InMemoryCategoryRepository
from .message_queue import InMemoryMessageQueue


class InMemoryUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.todos = InMemoryTodoRepository()
        self.users = InMemoryUserRepository()
        self.categories = InMemoryCategoryRepository()
        self.mq = InMemoryMessageQueue()
        self.committed = False

    def __enter__(self):
        return super().__enter__()

    def __exit__(self, exc_type, exc_val, traceback):
        # No rollback needed for in-memory implementation
        super().__exit__(exc_type, exc_val, traceback)

    def commit(self):
        self.committed = True

    def rollback(self):
        # No-op for in-memory
        pass
