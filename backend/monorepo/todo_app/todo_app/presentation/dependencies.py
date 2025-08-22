from ..application.services import TodoService
from ..infrastructure.repositories import SQLAlchemyTodoRepository
from ..infrastructure.database import get_db
from ..application.message_queue import PgmqMessageQueue
from sqlalchemy.orm import Session
from fastapi import Depends


def get_todo_service(db_session: Session = Depends(get_db)) -> TodoService:
    repo = SQLAlchemyTodoRepository(db_session)
    mq = PgmqMessageQueue(db_session)
    return TodoService(todo_repo=repo, mq=mq)
