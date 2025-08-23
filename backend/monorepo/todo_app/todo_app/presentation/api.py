from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from . import schemas
from .dependencies import (
    get_todo_service,
    get_auth_service,
    get_current_user,
    get_category_service,
)
from ..application.services import TodoService
from ..application.auth_service import AuthService
from ..application.category_service import CategoryService
from ..domain.models import User
from typing import List

app = FastAPI()


# --- Auth Endpoints ---
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = auth_service.authenticate_user(
        username=form_data.username, plain_password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_service.create_access_token_for_user(user=user)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: schemas.UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        user = auth_service.register_user(
            username=user_in.username, plain_password=user_in.password
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return user


# --- Category Endpoints ---
@app.post("/categories/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_in: schemas.CategoryCreate,
    category_service: CategoryService = Depends(get_category_service),
    current_user: User = Depends(get_current_user),
):
    return category_service.create_category(
        name=category_in.name, user_id=current_user.id
    )


@app.get("/categories/", response_model=List[schemas.Category])
async def list_categories(
    category_service: CategoryService = Depends(get_category_service),
    current_user: User = Depends(get_current_user),
):
    return category_service.list_categories_by_user(user_id=current_user.id)


@app.put("/categories/{category_id}", response_model=schemas.Category)
async def update_category(
    category_id: int,
    category_in: schemas.CategoryUpdate,
    category_service: CategoryService = Depends(get_category_service),
    current_user: User = Depends(get_current_user),
):
    updated_category = category_service.update_category(
        category_id=category_id, user_id=current_user.id, name=category_in.name
    )
    if not updated_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated_category


@app.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
    current_user: User = Depends(get_current_user),
):
    success = category_service.delete_category(
        category_id=category_id, user_id=current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return {}


# --- Todo Endpoints ---
@app.post("/todos/", status_code=status.HTTP_202_ACCEPTED)
async def create_todo(
    todo: schemas.TodoCreate,
    todo_service: TodoService = Depends(get_todo_service),
    current_user: User = Depends(get_current_user),
):
    todo_service.create_todo(task=todo.task, user_id=current_user.id)
    return {"message": "Todo creation request received"}


@app.get("/todos/", response_model=List[schemas.Todo])
async def read_todos(
    todo_service: TodoService = Depends(get_todo_service),
    current_user: User = Depends(get_current_user),
):
    todos = todo_service.get_all_todos(user_id=current_user.id)
    return todos


@app.get("/todos/{todo_id}", response_model=schemas.Todo)
async def read_todo(
    todo_id: int,
    todo_service: TodoService = Depends(get_todo_service),
    current_user: User = Depends(get_current_user),
):
    todo = todo_service.get_todo(todo_id=todo_id, user_id=current_user.id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.put("/todos/{todo_id}", response_model=schemas.Todo)
async def update_todo(
    todo_id: int,
    todo_update: schemas.TodoUpdate,
    todo_service: TodoService = Depends(get_todo_service),
    current_user: User = Depends(get_current_user),
):
    updated_todo = todo_service.update_todo(
        todo_id=todo_id,
        user_id=current_user.id,
        task=todo_update.task,
        is_completed=todo_update.is_completed,
    )
    if updated_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated_todo


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    todo_service: TodoService = Depends(get_todo_service),
    current_user: User = Depends(get_current_user),
):
    success = todo_service.delete_todo(todo_id=todo_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {}


@app.post("/todos/{todo_id}/complete", status_code=status.HTTP_202_ACCEPTED)
async def complete_todo(
    todo_id: int,
    todo_service: TodoService = Depends(get_todo_service),
    current_user: User = Depends(get_current_user),
):
    todo_service.complete_todo(todo_id=todo_id, user_id=current_user.id)
    return {"message": "Todo completion request received"}


# --- SubTask Endpoints ---
@app.post(
    "/todos/{todo_id}/subtasks/",
    response_model=schemas.SubTask,
    status_code=status.HTTP_201_CREATED,
)
async def create_subtask_for_todo(
    todo_id: int,
    subtask: schemas.SubTaskCreate,
    todo_service: TodoService = Depends(get_todo_service),
    current_user: User = Depends(get_current_user),
):
    new_subtask = todo_service.add_subtask_to_todo(
        user_id=current_user.id, todo_id=todo_id, subtask_task=subtask.task
    )
    if new_subtask is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return new_subtask


@app.put("/todos/{todo_id}/subtasks/{subtask_id}", response_model=schemas.SubTask)
async def update_subtask(
    todo_id: int,
    subtask_id: int,
    subtask_update: schemas.SubTaskUpdate,
    todo_service: TodoService = Depends(get_todo_service),
    current_user: User = Depends(get_current_user),
):
    updated_subtask = todo_service.update_subtask(
        user_id=current_user.id,
        todo_id=todo_id,
        subtask_id=subtask_id,
        task=subtask_update.task,
        is_completed=subtask_update.is_completed,
    )
    if updated_subtask is None:
        raise HTTPException(status_code=404, detail="Subtask or parent Todo not found")
    return updated_subtask


@app.delete(
    "/todos/{todo_id}/subtasks/{subtask_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_subtask(
    todo_id: int,
    subtask_id: int,
    todo_service: TodoService = Depends(get_todo_service),
    current_user: User = Depends(get_current_user),
):
    success = todo_service.delete_subtask(
        user_id=current_user.id, todo_id=todo_id, subtask_id=subtask_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Subtask or parent Todo not found")
    return {}


# --- Todo-Category Assignment Endpoints ---
@app.post("/todos/{todo_id}/categories/{category_id}", response_model=schemas.Todo)
async def assign_category_to_todo(
    todo_id: int,
    category_id: int,
    todo_service: TodoService = Depends(get_todo_service),
    current_user: User = Depends(get_current_user),
):
    updated_todo = todo_service.assign_category_to_todo(
        user_id=current_user.id, todo_id=todo_id, category_id=category_id
    )
    if updated_todo is None:
        raise HTTPException(status_code=404, detail="Todo or Category not found")
    return updated_todo


@app.delete(
    "/todos/{todo_id}/categories/{category_id}", response_model=schemas.Todo
)
async def remove_category_from_todo(
    todo_id: int,
    category_id: int,
    todo_service: TodoService = Depends(get_todo_service),
    current_user: User = Depends(get_current_user),
):
    updated_todo = todo_service.remove_category_from_todo(
        user_id=current_user.id, todo_id=todo_id, category_id=category_id
    )
    if updated_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated_todo
