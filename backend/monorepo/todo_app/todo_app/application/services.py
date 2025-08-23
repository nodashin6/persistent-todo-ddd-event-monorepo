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


class TodoWorkerService:
    def __init__(self, todo_repo: TodoRepository):
        self.todo_repo = todo_repo

    def create_todo(self, task: str):
        todo = Todo.create(task=task)
        self.todo_repo.add(todo)

    def complete_todo(self, todo_id: int):
        todo = self.todo_repo.get(todo_id)
        if todo:
            todo.complete()
            self.todo_repo.update(todo)
