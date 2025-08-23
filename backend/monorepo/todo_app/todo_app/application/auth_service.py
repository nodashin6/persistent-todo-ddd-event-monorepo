from .unit_of_work import AbstractUnitOfWork
from ..domain.models import User
from . import security
from typing import Optional


class AuthService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    def register_user(self, username: str, plain_password: str) -> User:
        with self.uow:
            existing_user = self.uow.users.get_by_username(username)
            if existing_user:
                raise ValueError("Username already exists")

            user = User.create(username=username, plain_password=plain_password)
            new_user = self.uow.users.add(user)
            self.uow.commit()
            return new_user

    def authenticate_user(
        self, username: str, plain_password: str
    ) -> Optional[User]:
        with self.uow:
            user = self.uow.users.get_by_username(username)
            if not user:
                return None
            if not user.verify_password(plain_password):
                return None
            return user

    def create_access_token_for_user(self, user: User) -> str:
        access_token = security.create_access_token(data={"sub": user.username})
        return access_token
