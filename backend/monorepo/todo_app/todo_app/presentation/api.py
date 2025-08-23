from fastapi import FastAPI, Depends
from . import schemas
from .dependencies import get_todo_service
from ..application.services import TodoService

app = FastAPI()


@app.post("/todos/")
async def create_todo(
    todo: schemas.TodoCreate,
    todo_service: TodoService = Depends(get_todo_service),
):
    todo_service.create_todo(task=todo.task)
    return {"message": "Todo creation request received"}


@app.post("/todos/{todo_id}/complete")
async def complete_todo(
    todo_id: int,
    todo_service: TodoService = Depends(get_todo_service),
):
    todo_service.complete_todo(todo_id=todo_id)
    return {"message": "Todo completion request received"}


@app.get("/todos/")
async def read_todos(
    todo_service: TodoService = Depends(get_todo_service),
):
    todos = todo_service.get_all_todos()
    return todos
