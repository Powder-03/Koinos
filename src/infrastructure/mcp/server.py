from fastmcp import FastMCP
from typing import Optional
from datetime import date
from src.domain.models import Expense, ExpenseCategory
from src.infrastructure.database.connection import async_session_maker
from src.infrastructure.database.repository import PostgresExpenseRepository

mcp = FastMCP("ExpenseTrackerDualMode")

@mcp.tool()
async def add_expense(
    amount: float, 
    category: str, 
    expense_date: str, 
    description: Optional[str] = None
) -> str:
    """Log or add a new expense."""
    try:
        # Validate category and date
        cat_enum = ExpenseCategory(category.capitalize())
        parsed_date = date.fromisoformat(expense_date)
        
        async with async_session_maker() as session:
            repo = PostgresExpenseRepository(session)
            expense = Expense(
                amount=amount, 
                category=cat_enum, 
                date=parsed_date, 
                description=description
            )
            added_expense = await repo.add(expense)
            return f"Successfully logged expense. ID: {added_expense.id}, Amount: {amount}, Category: {cat_enum.value}, Date: {parsed_date}"
    except ValueError as e:
        return f"Validation error: {str(e)}. Valid categories are: {[c.value for c in ExpenseCategory]}."
    except Exception as e:
        return f"Error adding expense: {str(e)}"

@mcp.tool()
async def search_expenses(
    category: Optional[str] = None, 
    expense_date: Optional[str] = None, 
    amount: Optional[float] = None
) -> str:
    """
    Search the database for expenses. 
    Always use this to confirm an expense ID before updating or deleting.
    """
    kwargs = {}
    try:
        if category:
            kwargs["category"] = ExpenseCategory(category.capitalize()).value
        if expense_date:
            kwargs["date"] = date.fromisoformat(expense_date)
        if amount:
            kwargs["amount"] = amount

        async with async_session_maker() as session:
            repo = PostgresExpenseRepository(session)
            expenses = await repo.search(**kwargs)
            
            if not expenses:
                return "No expenses found matching those criteria."

            summary = [f"Found {len(expenses)} expense(s):"]
            for e in expenses:
                desc = f" - '{e.description}'" if e.description else ""
                summary.append(f"  [ID: {e.id}] {e.category.value}: ${e.amount} on {e.date}{desc}")
            
            return "\n".join(summary)
    except ValueError as e:
        return f"Search parameter invalid: {e}"

@mcp.tool()
async def update_expense(
    expense_id: int, 
    amount: Optional[float] = None, 
    category: Optional[str] = None, 
    expense_date: Optional[str] = None, 
    description: Optional[str] = None
) -> str:
    """Update an existing expense. You MUST know the exact ID."""
    update_data = {}
    try:
        if amount is not None:
            update_data["amount"] = amount
        if category is not None:
            update_data["category"] = ExpenseCategory(category.capitalize()).value
        if expense_date is not None:
            update_data["date"] = date.fromisoformat(expense_date)
        if description is not None:
            update_data["description"] = description

        if not update_data:
            return "No modification fields provided."

        async with async_session_maker() as session:
            repo = PostgresExpenseRepository(session)
            updated_expense = await repo.update(expense_id, update_data)
            
            if updated_expense:
                return f"Successfully updated expense ID {expense_id}."
            return f"Error: Expense with ID {expense_id} not found."
    except ValueError as e:
         return f"Validation error: {str(e)}."

@mcp.tool()
async def delete_expense(expense_id: int) -> str:
    """Delete an expense. You MUST know the exact ID."""
    async with async_session_maker() as session:
        repo = PostgresExpenseRepository(session)
        success = await repo.delete(expense_id)
        if success:
            return f"Successfully deleted expense ID {expense_id}."
        return f"Error: Expense with ID {expense_id} not found."
