from ..domain.models import Todo
from ..domain.repositories import TodoRepository
from . import message_queue
import json


class TodoService:
    def __init__(self, todo_repo: TodoRepository, mq: message_queue.MessageQueue):
        self.todo_repo = todo_repo
        self.mq = mq

    def create_todo(self, task: str):
        message = {"action": "create", "task": task}
        self.mq.send("todo_queue", message)

    def complete_todo(self, todo_id: int):
        message = {"action": "complete", "todo_id": todo_id}
        self.mq.send("todo_queue", message)

    def get_all_todos(self):
        return self.todo_repo.list()


from ..infrastructure.unit_of_work import AbstractUnitOfWork


class TodoWorkerService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    def create_todo(self, task: str):
        # The UoW context is managed by the caller (the worker entrypoint)
        todo = Todo.create(task=task)
        self.uow.todos.add(todo)

    def complete_todo(self, todo_id: int):
        # The UoW context is managed by the caller (the worker entrypoint)
        todo = self.uow.todos.get(todo_id)
        if todo:
            todo.complete()
