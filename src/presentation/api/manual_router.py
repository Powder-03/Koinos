from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from src.infrastructure.database.connection import get_db_session
from src.infrastructure.database.repository import PostgresExpenseRepository
from src.domain.models import Expense

router = APIRouter(prefix="/api/manual", tags=["Manual Mode"])

@router.post("/", response_model=Expense)
async def create_manual_expense(expense: Expense, session: AsyncSession = Depends(get_db_session)):
    repo = PostgresExpenseRepository(session)
    return await repo.add(expense)

@router.get("/", response_model=List[Expense])
async def get_manual_expenses(
    category: Optional[str] = None,
    session: AsyncSession = Depends(get_db_session)
):
    repo = PostgresExpenseRepository(session)
    kwargs = {}
    if category:
        kwargs["category"] = category
    return await repo.search(**kwargs)

@router.put("/{expense_id}", response_model=Expense)
async def update_manual_expense(
    expense_id: int, 
    expense: Expense, 
    session: AsyncSession = Depends(get_db_session)
):
    repo = PostgresExpenseRepository(session)
    expense_data = expense.model_dump(exclude_unset=True, exclude={"id"})
    updated = await repo.update(expense_id, expense_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Expense not found")
    return updated

@router.delete("/{expense_id}")
async def delete_manual_expense(expense_id: int, session: AsyncSession = Depends(get_db_session)):
    repo = PostgresExpenseRepository(session)
    success = await repo.delete(expense_id)
    if not success:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}
