from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from src.domain.models import Expense
from src.application.interfaces.repository import ExpenseRepository
from src.infrastructure.database.models import ExpenseORM

class PostgresExpenseRepository(ExpenseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, orm_model: ExpenseORM) -> Expense:
        return Expense(
            id=str(orm_model.id),
            user_id=orm_model.user_id,
            amount=orm_model.amount,
            category=orm_model.category,
            description=orm_model.description,
            date=orm_model.date
        )

    async def add(self, expense: Expense) -> Expense:
        orm_expense = ExpenseORM(
            user_id=expense.user_id,
            amount=expense.amount,
            category=expense.category,
            description=expense.description,
            date=expense.date
        )
        self.session.add(orm_expense)
        await self.session.commit()
        await self.session.refresh(orm_expense)
        return self._to_domain(orm_expense)

    async def search(self, user_id: str, **kwargs) -> List[Expense]:
        stmt = select(ExpenseORM).where(ExpenseORM.user_id == user_id).order_by(ExpenseORM.date.desc())
        for key, value in kwargs.items():
            if hasattr(ExpenseORM, key) and value is not None:
                stmt = stmt.where(getattr(ExpenseORM, key) == value)

        result = await self.session.execute(stmt)
        orm_expenses = result.scalars().all()
        return [self._to_domain(e) for e in orm_expenses]

    async def update(self, expense_id: str, user_id: str, expense_data: dict) -> Optional[Expense]:
        stmt = (
            update(ExpenseORM)
            .where(ExpenseORM.id == UUID(expense_id))
            .where(ExpenseORM.user_id == user_id)
            .values(**expense_data)
            .returning(ExpenseORM)
        )
        result = await self.session.execute(stmt)
        updated_orm = result.scalar_one_or_none()
        await self.session.commit()

        if updated_orm:
            return self._to_domain(updated_orm)
        return None

    async def delete(self, expense_id: str, user_id: str) -> bool:
        stmt = (
            delete(ExpenseORM)
            .where(ExpenseORM.id == UUID(expense_id))
            .where(ExpenseORM.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

