from ..domain.models import Todo
from ..domain.repositories import TodoRepository
from . import message_queue
import json


from .unit_of_work import AbstractUnitOfWork


class TodoService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    def create_todo(self, task: str, user_id: int):
        # We are creating the domain model here, but the worker will do the actual
        # database insertion. The message needs to contain all necessary data.
        message = {"action": "create", "task": task, "user_id": user_id}
        with self.uow:
            self.uow.mq.send("todo_queue", message)
            self.uow.commit()

    def complete_todo(self, todo_id: int, user_id: int):
        # The worker will handle the completion logic, including checking ownership.
        message = {"action": "complete", "todo_id": todo_id, "user_id": user_id}
        with self.uow:
            self.uow.mq.send("todo_queue", message)
            self.uow.commit()

    def get_all_todos(self, user_id: int):
        with self.uow:
            return self.uow.todos.list(user_id=user_id)

    def get_todo(self, todo_id: int, user_id: int):
        with self.uow:
            return self.uow.todos.get(todo_id=todo_id, user_id=user_id)

    def update_todo(
        self,
        todo_id: int,
        user_id: int,
        task: str | None,
        is_completed: bool | None,
    ):
        with self.uow:
            todo = self.uow.todos.get(todo_id=todo_id, user_id=user_id)
            if not todo:
                return None

            if task is not None:
                todo.task = task
            if is_completed is not None:
                if is_completed:
                    todo.complete()
                else:
                    todo.uncomplete()

            updated_todo = self.uow.todos.update(todo)
            self.uow.commit()
            return updated_todo

    def delete_todo(self, todo_id: int, user_id: int):
        with self.uow:
            success = self.uow.todos.delete(todo_id=todo_id, user_id=user_id)
            self.uow.commit()
            return success

    def add_subtask_to_todo(self, user_id: int, todo_id: int, subtask_task: str):
        with self.uow:
            todo = self.uow.todos.get(todo_id=todo_id, user_id=user_id)
            if not todo:
                return None

            original_subtask_count = len(todo.subtasks)
            # This adds the subtask to the todo's list of subtasks
            todo.add_subtask(task=subtask_task)

            # The update method will persist the new subtask and assign it an ID
            updated_todo = self.uow.todos.update(todo)
            self.uow.commit()

            # Find the newly added subtask (it's the last one)
            if len(updated_todo.subtasks) > original_subtask_count:
                return updated_todo.subtasks[-1]
            return None # Should not happen if update is correct

    def update_subtask(
        self,
        user_id: int,
        todo_id: int,
        subtask_id: int,
        task: str | None,
        is_completed: bool | None,
    ):
        with self.uow:
            todo = self.uow.todos.get(todo_id=todo_id, user_id=user_id)
            if not todo:
                return None

            subtask = next((st for st in todo.subtasks if st.id == subtask_id), None)
            if not subtask:
                return None

            if task is not None:
                subtask.task = task
            if is_completed is not None:
                subtask.is_completed = is_completed

            self.uow.todos.update(todo)
            self.uow.commit()
            return subtask

    def delete_subtask(self, user_id: int, todo_id: int, subtask_id: int):
        with self.uow:
            todo = self.uow.todos.get(todo_id=todo_id, user_id=user_id)
            if not todo:
                return False

            original_len = len(todo.subtasks)
            todo.subtasks = [st for st in todo.subtasks if st.id != subtask_id]

            if len(todo.subtasks) == original_len:
                return False # Subtask not found

            self.uow.todos.update(todo)
            self.uow.commit()
            return True

    def assign_category_to_todo(self, user_id: int, todo_id: int, category_id: int):
        with self.uow:
            todo = self.uow.todos.get(todo_id, user_id)
            category = self.uow.categories.get(category_id, user_id)

            if not todo or not category:
                return None

            todo.assign_category(category)
            self.uow.todos.update(todo)
            self.uow.commit()
            return todo

    def remove_category_from_todo(self, user_id: int, todo_id: int, category_id: int):
        with self.uow:
            todo = self.uow.todos.get(todo_id, user_id)
            if not todo:
                return None

            todo.remove_category(category_id)
            self.uow.todos.update(todo)
            self.uow.commit()
            return todo


class TodoWorkerService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    def create_todo(self, task: str, user_id: int):
        # The UoW context is managed by the caller (the worker entrypoint)
        todo = Todo.create(task=task, user_id=user_id)
        self.uow.todos.add(todo)

    def complete_todo(self, todo_id: int, user_id: int):
        # The UoW context is managed by the caller (the worker entrypoint)
        todo = self.uow.todos.get(todo_id, user_id)
        if todo:
            todo.complete()
