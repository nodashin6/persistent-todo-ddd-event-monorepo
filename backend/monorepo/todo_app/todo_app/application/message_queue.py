from abc import ABC, abstractmethod
import json
from sqlalchemy.orm import Session
from sqlalchemy import text


class MessageQueue(ABC):
    @abstractmethod
    def send(self, queue_name: str, message: dict):
        raise NotImplementedError


class PgmqMessageQueue(MessageQueue):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def send(self, queue_name: str, message: dict):
        self.db_session.execute(
            text(f"SELECT pgmq.send(:queue_name, :message::jsonb)"),
            {"queue_name": queue_name, "message": json.dumps(message)},
        )
        self.db_session.commit()
