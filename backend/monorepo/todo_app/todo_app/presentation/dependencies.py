from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from ..application.services import TodoService
from ..application.auth_service import AuthService
from ..application.category_service import CategoryService
from ..infrastructure.unit_of_work import AbstractUnitOfWork, SQLAlchemyUnitOfWork
from ..application import security
from ..domain.models import User
from . import schemas

# This needs to be defined here to avoid circular imports with api.py
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_uow() -> AbstractUnitOfWork:
    """
    Dependency to get a Unit of Work instance.
    This will be created once per request.
    """
    return SQLAlchemyUnitOfWork()


def get_todo_service(uow: AbstractUnitOfWork = Depends(get_uow)) -> TodoService:
    return TodoService(uow=uow)


def get_auth_service(uow: AbstractUnitOfWork = Depends(get_uow)) -> AuthService:
    return AuthService(uow=uow)


def get_category_service(uow: AbstractUnitOfWork = Depends(get_uow)) -> CategoryService:
    return CategoryService(uow=uow)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = security.decode_access_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    with auth_service.uow:
        user = auth_service.uow.users.get_by_username(username)
        if user is None:
            raise credentials_exception
        return user
