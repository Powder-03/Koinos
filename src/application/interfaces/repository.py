from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models import Expense

class ExpenseRepository(ABC):
    @abstractmethod
    async def add(self, expense: Expense) -> Expense:
        pass

    @abstractmethod
    async def search(self, user_id: str, **kwargs) -> List[Expense]:
        pass

    @abstractmethod
    async def update(self, expense_id: str, user_id: str, expense_data: dict) -> Optional[Expense]:
        pass

    @abstractmethod
    async def delete(self, expense_id: str, user_id: str) -> bool:
        pass
