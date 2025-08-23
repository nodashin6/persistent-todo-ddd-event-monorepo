from pydantic import BaseModel
import datetime
from typing import List


class TodoBase(BaseModel):
    task: str


class TodoCreate(TodoBase):
    pass


class TodoUpdate(TodoBase):
    task: str | None = None
    is_completed: bool | None = None


class SubTaskBase(BaseModel):
    task: str


class SubTaskCreate(SubTaskBase):
    pass


class SubTaskUpdate(SubTaskBase):
    task: str | None = None
    is_completed: bool | None = None


class SubTask(SubTaskBase):
    id: int
    is_completed: bool
    todo_id: int

    class Config:
        orm_mode = True


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    name: str | None = None


class Category(CategoryBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class Todo(TodoBase):
    id: int
    is_completed: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    subtasks: List[SubTask] = []
    categories: List[Category] = []

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
