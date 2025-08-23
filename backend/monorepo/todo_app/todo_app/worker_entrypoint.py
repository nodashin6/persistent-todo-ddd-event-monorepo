import time
import json
from sqlalchemy.orm import Session
from sqlalchemy import text
from .application.services import TodoWorkerService
from .infrastructure.repositories import SQLAlchemyTodoRepository
from .infrastructure.database import get_db


def process_message(db_session: Session, msg: dict):
    repo = SQLAlchemyTodoRepository(db_session)
    worker_service = TodoWorkerService(repo)

    action = msg.get("action")
    if action == "create":
        worker_service.create_todo(task=msg["task"])
    elif action == "complete":
        worker_service.complete_todo(todo_id=msg["todo_id"])
    else:
        print(f"Unknown action: {action}")


def main():
    print("Starting worker...")
    while True:
        db_session = next(get_db())
        try:
            result = db_session.execute(
                text("SELECT * FROM pgmq.read('todo_queue', 1, 1)")
            ).first()
            if result:
                msg_id, _, _, _, message = result
                print(f"Processing message {msg_id}: {message}")
                try:
                    process_message(db_session, json.loads(message))
                    db_session.execute(
                        text("SELECT pgmq.delete('todo_queue', :msg_id)"),
                        {"msg_id": msg_id},
                    )
                    db_session.commit()
                    print(f"Message {msg_id} processed and deleted.")
                except Exception as e:
                    print(f"Error processing message {msg_id}: {e}")
            else:
                print("No messages in queue. Waiting...")
                time.sleep(5)
        finally:
            db_session.close()


if __name__ == "__main__":
    main()
