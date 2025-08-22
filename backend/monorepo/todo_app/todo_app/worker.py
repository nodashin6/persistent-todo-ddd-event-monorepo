import time
import json
from sqlalchemy.orm import Session
from sqlalchemy import text
from . import models, db
import datetime


def handle_create_todo(db_session: Session, msg: dict):
    epoch_now = int(time.time())
    new_todo = models.Todo(
        task=msg["task"],
        is_completed=False,
        created_at=datetime.datetime.now(datetime.timezone.utc),
        updated_at=epoch_now,
    )
    db_session.add(new_todo)
    db_session.commit()
    db_session.refresh(new_todo)

    new_p_todo = models.PTodo(
        todo_id=new_todo.id,
        task=new_todo.task,
        is_completed=new_todo.is_completed,
        created_at=new_todo.created_at,
        updated_at=new_todo.updated_at,
        validate_from=new_todo.updated_at,
        validate_to=None,
    )
    db_session.add(new_p_todo)
    db_session.commit()


def handle_complete_todo(db_session: Session, msg: dict):
    todo_id = msg["todo_id"]
    epoch_now = int(time.time())

    # Find the todo to update
    todo_to_update = (
        db_session.query(models.Todo).filter(models.Todo.id == todo_id).first()
    )
    if not todo_to_update:
        print(f"Todo with id {todo_id} not found.")
        return

    # Update the todo
    todo_to_update.is_completed = True
    todo_to_update.updated_at = epoch_now
    db_session.commit()

    # Invalidate the old p_todo record
    old_p_todo = (
        db_session.query(models.PTodo)
        .filter(models.PTodo.todo_id == todo_id, models.PTodo.validate_to == None)
        .first()
    )
    if old_p_todo:
        old_p_todo.validate_to = epoch_now
        db_session.commit()

    # Create the new p_todo record
    new_p_todo = models.PTodo(
        todo_id=todo_to_update.id,
        task=todo_to_update.task,
        is_completed=todo_to_update.is_completed,
        created_at=todo_to_update.created_at,
        updated_at=todo_to_update.updated_at,
        validate_from=epoch_now,
        validate_to=None,
    )
    db_session.add(new_p_todo)
    db_session.commit()


def process_message(db_session: Session, msg: dict):
    action = msg.get("action")
    if action == "create":
        handle_create_todo(db_session, msg)
    elif action == "complete":
        handle_complete_todo(db_session, msg)
    else:
        print(f"Unknown action: {action}")


def main():
    print("Starting worker...")
    while True:
        db_session = next(db.get_db())
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
