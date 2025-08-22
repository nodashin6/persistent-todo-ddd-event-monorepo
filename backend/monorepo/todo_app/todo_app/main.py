import json
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from . import models, db, schemas

app = FastAPI()


@app.post("/todos/")
async def create_todo(
    todo: schemas.TodoCreate, db_session: Session = Depends(db.get_db)
):
    message = {"action": "create", "task": todo.task}

    # Send a message to the queue using raw SQL
    db_session.execute(
        text("SELECT pgmq.send('todo_queue', :message::jsonb)"),
        {"message": json.dumps(message)},
    )
    db_session.commit()

    return {"message": "Todo creation request received"}


@app.post("/todos/{todo_id}/complete")
async def complete_todo(todo_id: int, db_session: Session = Depends(db.get_db)):
    message = {"action": "complete", "todo_id": todo_id}

    # Send a message to the queue using raw SQL
    db_session.execute(
        text("SELECT pgmq.send('todo_queue', :message::jsonb)"),
        {"message": json.dumps(message)},
    )
    db_session.commit()

    return {"message": "Todo completion request received"}


@app.get("/todos/")
async def read_todos(db_session: Session = Depends(db.get_db)):
    todos = db_session.query(models.Todo).all()
    return todos
