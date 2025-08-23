from sqlalchemy.orm import Session
from typing import Optional, List
from ..domain.models import Todo, User, SubTask, Category
from ..domain.repositories import TodoRepository, UserRepository, CategoryRepository
from ..domain.events import TodoCreated, UserCreated
from . import orm
import time


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def add(self, user: User) -> User:
        orm_user = orm.User(
            username=user.username,
            hashed_password=user.hashed_password,
        )
        self.db_session.add(orm_user)
        self.db_session.flush()
        self.db_session.refresh(orm_user)

        domain_user = self._to_domain(orm_user)
        domain_user._add_domain_event(
            UserCreated(user_id=domain_user.id, username=domain_user.username)
        )
        return domain_user

    def get_by_username(self, username: str):
        orm_user = (
            self.db_session.query(orm.User).filter(orm.User.username == username).first()
        )
        if orm_user:
            return self._to_domain(orm_user)
        return None

    def _to_domain(self, orm_user: orm.User) -> User:
        return User(
            id=orm_user.id,
            username=orm_user.username,
            hashed_password=orm_user.hashed_password,
        )


class SQLAlchemyCategoryRepository(CategoryRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def add(self, category: Category) -> Category:
        orm_category = orm.Category(
            name=category.name,
            user_id=category.user_id,
        )
        self.db_session.add(orm_category)
        self.db_session.flush()
        self.db_session.refresh(orm_category)
        return self._to_domain(orm_category)

    def get(self, category_id: int, user_id: int) -> Optional[Category]:
        orm_category = (
            self.db_session.query(orm.Category)
            .filter(orm.Category.id == category_id, orm.Category.user_id == user_id)
            .first()
        )
        return self._to_domain(orm_category) if orm_category else None

    def list_by_user(self, user_id: int) -> List[Category]:
        orm_categories = (
            self.db_session.query(orm.Category)
            .filter(orm.Category.user_id == user_id)
            .all()
        )
        return [self._to_domain(cat) for cat in orm_categories]

    def update(self, category: Category) -> Optional[Category]:
        orm_category = (
            self.db_session.query(orm.Category)
            .filter(orm.Category.id == category.id, orm.Category.user_id == category.user_id)
            .first()
        )
        if not orm_category:
            return None
        orm_category.name = category.name
        return self._to_domain(orm_category)

    def delete(self, category_id: int, user_id: int) -> bool:
        orm_category = (
            self.db_session.query(orm.Category)
            .filter(orm.Category.id == category_id, orm.Category.user_id == user_id)
            .first()
        )
        if not orm_category:
            return False
        self.db_session.delete(orm_category)
        return True

    def _to_domain(self, orm_category: orm.Category) -> Category:
        return Category(
            id=orm_category.id,
            user_id=orm_category.user_id,
            name=orm_category.name,
        )


class SQLAlchemyTodoRepository(TodoRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def add(self, todo: Todo) -> Todo:
        orm_todo = orm.Todo(
            task=todo.task,
            is_completed=todo.is_completed,
            created_at=todo.created_at,
            updated_at=todo.updated_at,
            user_id=todo.user_id,
        )
        # Handle categories
        if todo.categories:
            category_ids = [cat.id for cat in todo.categories if cat.id is not None]
            orm_categories = self.db_session.query(orm.Category).filter(orm.Category.id.in_(category_ids)).all()
            orm_todo.categories = orm_categories

        self.db_session.add(orm_todo)
        self.db_session.flush()
        self.db_session.refresh(orm_todo)

        domain_todo = self._to_domain(orm_todo)
        domain_todo._add_domain_event(
            TodoCreated(todo_id=domain_todo.id, task=domain_todo.task)
        )
        return domain_todo

    def get(self, todo_id: int, user_id: int):
        orm_todo = (
            self.db_session.query(orm.Todo)
            .filter(orm.Todo.id == todo_id, orm.Todo.user_id == user_id)
            .first()
        )
        if orm_todo:
            return self._to_domain(orm_todo)
        return None

    def list(self, user_id: int):
        return [
            self._to_domain(orm_todo)
            for orm_todo in self.db_session.query(orm.Todo)
            .filter(orm.Todo.user_id == user_id)
            .all()
        ]

    def update(self, todo: Todo):
        orm_todo = (
            self.db_session.query(orm.Todo)
            .filter(orm.Todo.id == todo.id, orm.Todo.user_id == todo.user_id)
            .first()
        )
        if not orm_todo:
            return None

        orm_todo.task = todo.task
        orm_todo.is_completed = todo.is_completed
        orm_todo.updated_at = todo.updated_at

        orm_todo.subtasks.clear()
        for subtask in todo.subtasks:
            orm_todo.subtasks.append(
                orm.SubTask(
                    id=subtask.id,
                    task=subtask.task,
                    is_completed=subtask.is_completed,
                )
            )

        # Sync categories
        category_ids = [cat.id for cat in todo.categories if cat.id is not None]
        orm_categories = self.db_session.query(orm.Category).filter(orm.Category.id.in_(category_ids)).all()
        orm_todo.categories = orm_categories

        return self._to_domain(orm_todo)

    def delete(self, todo_id: int, user_id: int) -> bool:
        orm_todo = (
            self.db_session.query(orm.Todo)
            .filter(orm.Todo.id == todo_id, orm.Todo.user_id == user_id)
            .first()
        )
        if not orm_todo:
            return False

        self.db_session.delete(orm_todo)
        return True

    def _to_domain_subtask(self, orm_subtask: orm.SubTask) -> SubTask:
        return SubTask(
            id=orm_subtask.id,
            todo_id=orm_subtask.todo_id,
            task=orm_subtask.task,
            is_completed=orm_subtask.is_completed,
        )

    def _to_domain_category(self, orm_category: orm.Category) -> Category:
        return Category(
            id=orm_category.id,
            user_id=orm_category.user_id,
            name=orm_category.name,
        )

    def _to_domain(self, orm_todo: orm.Todo) -> Todo:
        return Todo(
            id=orm_todo.id,
            user_id=orm_todo.user_id,
            task=orm_todo.task,
            is_completed=orm_todo.is_completed,
            created_at=orm_todo.created_at,
            updated_at=orm_todo.updated_at,
            subtasks=[self._to_domain_subtask(st) for st in orm_todo.subtasks],
            categories=[self._to_domain_category(cat) for cat in orm_todo.categories],
        )
