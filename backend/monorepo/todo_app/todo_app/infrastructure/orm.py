from sqlalchemy import Column, Integer, String, Boolean, BigInteger, Text, TIMESTAMP, ForeignKey, Table
from sqlalchemy.orm import relationship
from .database import Base


todo_category_association = Table(
    "todo_category_association",
    Base.metadata,
    Column("todo_id", BigInteger, ForeignKey("todos.id"), primary_key=True),
    Column("category_id", BigInteger, ForeignKey("categories.id"), primary_key=True),
)


class Category(Base):
    __tablename__ = "categories"
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)

    owner = relationship("User")
    todos = relationship("Todo", secondary=todo_category_association, back_populates="categories")


class Todo(Base):
    __tablename__ = "todos"

    id = Column(BigInteger, primary_key=True, index=True)
    task = Column(Text, nullable=False)
    is_completed = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="todos")
    subtasks = relationship("SubTask", back_populates="todo", cascade="all, delete-orphan")
    categories = relationship("Category", secondary=todo_category_association, back_populates="todos")


class SubTask(Base):
    __tablename__ = "subtasks"

    id = Column(BigInteger, primary_key=True, index=True)
    task = Column(Text, nullable=False)
    is_completed = Column(Boolean, default=False)
    todo_id = Column(BigInteger, ForeignKey("todos.id"), nullable=False)

    todo = relationship("Todo", back_populates="subtasks")


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    todos = relationship("Todo", back_populates="owner")


class PTodo(Base):
    __tablename__ = "p_todos"

    id = Column(BigInteger, primary_key=True, index=True)
    todo_id = Column(BigInteger, nullable=False)
    task = Column(Text, nullable=False)
    is_completed = Column(Boolean, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(BigInteger, nullable=False)
    validate_from = Column(BigInteger, nullable=False)
    validate_to = Column(BigInteger)
