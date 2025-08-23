from abc import ABC, abstractmethod
import json
from sqlalchemy.orm import Session
from sqlalchemy import text


class MessageQueue(ABC):
    @abstractmethod
    def send(self, queue_name: str, message: dict):
        raise NotImplementedError

    @abstractmethod
    def read(self, queue_name: str, count: int, visibility_timeout: int):
        raise NotImplementedError

    @abstractmethod
    def delete(self, queue_name: str, msg_id: int):
        raise NotImplementedError


class PgmqMessageQueue(MessageQueue):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def send(self, queue_name: str, message: dict):
        self.db_session.execute(
            text(f"SELECT pgmq.send(:queue_name, :message::jsonb)"),
            {"queue_name": queue_name, "message": json.dumps(message)},
        )
        # The commit is handled by the UoW

    def read(self, queue_name: str, count: int, visibility_timeout: int):
        result = self.db_session.execute(
            text(
                "SELECT * FROM pgmq.read(:queue_name, :count, :vt)"
            ),
            {
                "queue_name": queue_name,
                "count": count,
                "vt": visibility_timeout,
            },
        ).first()
        return result

    def delete(self, queue_name: str, msg_id: int):
        self.db_session.execute(
            text("SELECT pgmq.delete(:queue_name, :msg_id)"),
            {"queue_name": queue_name, "msg_id": msg_id},
        )
