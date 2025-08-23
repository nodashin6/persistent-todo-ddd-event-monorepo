from sqlalchemy.orm import Session
from ..domain.models import Todo
from ..domain.repositories import TodoRepository
from ..domain.events import TodoCreated
from . import orm
import time


class SQLAlchemyTodoRepository(TodoRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def add(self, todo: Todo) -> Todo:
        orm_todo = orm.Todo(
            task=todo.task,
            is_completed=todo.is_completed,
            created_at=todo.created_at,
            updated_at=todo.updated_at,
        )
        self.db_session.add(orm_todo)
        self.db_session.flush()  # Use flush to get the ID without committing
        self.db_session.refresh(orm_todo)

        # Now orm_todo.id is populated, create the domain event
        domain_todo = self._to_domain(orm_todo)
        domain_todo._add_domain_event(
            TodoCreated(todo_id=domain_todo.id, task=domain_todo.task)
        )
        # The commit will be handled by the Unit of Work
        return domain_todo

    def get(self, todo_id: int):
        orm_todo = (
            self.db_session.query(orm.Todo).filter(orm.Todo.id == todo_id).first()
        )
        if orm_todo:
            return self._to_domain(orm_todo)
        return None

    def list(self):
        return [
            self._to_domain(orm_todo)
            for orm_todo in self.db_session.query(orm.Todo).all()
        ]

    def update(self, todo: Todo):
        orm_todo = (
            self.db_session.query(orm.Todo).filter(orm.Todo.id == todo.id).first()
        )
        if not orm_todo:
            return None

        orm_todo.task = todo.task
        orm_todo.is_completed = todo.is_completed
        orm_todo.updated_at = todo.updated_at
        # The commit will be handled by the Unit of Work
        return self._to_domain(orm_todo)

    def _to_domain(self, orm_todo: orm.Todo) -> Todo:
        return Todo(
            id=orm_todo.id,
            task=orm_todo.task,
            is_completed=orm_todo.is_completed,
            created_at=orm_todo.created_at,
            updated_at=orm_todo.updated_at,
        )
