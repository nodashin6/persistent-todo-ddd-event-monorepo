import time
import json
from sqlalchemy import text
from .application.services import TodoWorkerService
from .infrastructure.unit_of_work import SQLAlchemyUnitOfWork


def process_message(uow: SQLAlchemyUnitOfWork, msg: dict):
    worker_service = TodoWorkerService(uow)
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
        try:
            with SQLAlchemyUnitOfWork() as uow:
                result = uow.session.execute(
                    text("SELECT * FROM pgmq.read('todo_queue', 1, 1)")
                ).first()

                if result:
                    msg_id, _, _, _, message_str = result
                    print(f"Processing message {msg_id}: {message_str}")

                    message_data = json.loads(message_str)
                    process_message(uow, message_data)

                    uow.session.execute(
                        text("SELECT pgmq.delete('todo_queue', :msg_id)"),
                        {"msg_id": msg_id},
                    )
                    uow.commit()
                    print(f"Message {msg_id} processed and deleted.")
                else:
                    # No commit needed if no message is processed
                    print("No messages in queue. Waiting...")

        except Exception as e:
            print(f"An error occurred: {e}")
            # The UoW will rollback automatically on exception

        time.sleep(5)


if __name__ == "__main__":
    main()
