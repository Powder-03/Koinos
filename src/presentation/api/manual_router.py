from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from src.infrastructure.database.connection import get_db_session
from src.infrastructure.database.repository import PostgresExpenseRepository
from src.infrastructure.auth.firebase import verify_firebase_token
from src.domain.models import Expense, ExpenseCreate, ExpenseResponse

router = APIRouter(prefix="/api/manual", tags=["Manual Mode"])

@router.post("/", status_code=201)
async def create_manual_expense(
    expense_in: ExpenseCreate,
    user_id: str = Depends(verify_firebase_token),
    session: AsyncSession = Depends(get_db_session)
):
    expense = Expense(user_id=user_id, **expense_in.model_dump())
    repo = PostgresExpenseRepository(session)
    saved = await repo.add(expense)
    return {
        "message": f"₹{saved.amount:.0f} added in {saved.category} for {saved.date}",
        "id": saved.id
    }

@router.get("/", response_model=List[ExpenseResponse])
async def get_manual_expenses(
    category: Optional[str] = None,
    user_id: str = Depends(verify_firebase_token),
    session: AsyncSession = Depends(get_db_session)
):
    repo = PostgresExpenseRepository(session)
    kwargs = {}
    if category:
        kwargs["category"] = category
    return await repo.search(user_id=user_id, **kwargs)

@router.put("/{expense_id}")
async def update_manual_expense(
    expense_id: str,
    expense_in: ExpenseCreate,
    user_id: str = Depends(verify_firebase_token),
    session: AsyncSession = Depends(get_db_session)
):
    repo = PostgresExpenseRepository(session)
    expense_data = expense_in.model_dump(exclude_unset=True)
    updated = await repo.update(expense_id, user_id, expense_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {
        "message": f"Expense updated — ₹{updated.amount:.0f} in {updated.category} for {updated.date}",
        "id": updated.id
    }

@router.delete("/{expense_id}")
async def delete_manual_expense(
    expense_id: str,
    user_id: str = Depends(verify_firebase_token),
    session: AsyncSession = Depends(get_db_session)
):
    repo = PostgresExpenseRepository(session)
    success = await repo.delete(expense_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}

