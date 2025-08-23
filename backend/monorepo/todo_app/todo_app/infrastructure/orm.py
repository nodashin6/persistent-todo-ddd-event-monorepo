from sqlalchemy import Column, Integer, String, Boolean, BigInteger, Text, TIMESTAMP
from .database import Base


class Todo(Base):
    __tablename__ = "todos"

    id = Column(BigInteger, primary_key=True, index=True)
    task = Column(Text, nullable=False)
    is_completed = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(BigInteger, nullable=False)


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
