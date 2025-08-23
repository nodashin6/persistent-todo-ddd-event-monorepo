from .unit_of_work import AbstractUnitOfWork
from ..domain.models import Category
from typing import List, Optional


class CategoryService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    def create_category(self, name: str, user_id: int) -> Category:
        with self.uow:
            # Optionally check for duplicate names for the same user
            category = Category(id=None, user_id=user_id, name=name)
            new_category = self.uow.categories.add(category)
            self.uow.commit()
            return new_category

    def get_category(self, category_id: int, user_id: int) -> Optional[Category]:
        with self.uow:
            return self.uow.categories.get(category_id=category_id, user_id=user_id)

    def list_categories_by_user(self, user_id: int) -> List[Category]:
        with self.uow:
            return self.uow.categories.list_by_user(user_id=user_id)

    def update_category(
        self, category_id: int, user_id: int, name: str
    ) -> Optional[Category]:
        with self.uow:
            category = self.uow.categories.get(category_id=category_id, user_id=user_id)
            if not category:
                return None
            category.name = name
            updated_category = self.uow.categories.update(category)
            self.uow.commit()
            return updated_category

    def delete_category(self, category_id: int, user_id: int) -> bool:
        with self.uow:
            success = self.uow.categories.delete(category_id=category_id, user_id=user_id)
            self.uow.commit()
            return success
