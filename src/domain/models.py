from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date as date_type
from enum import Enum

class ExpenseCategory(str, Enum):
    FOOD = "Food"
    TRANSPORT = "Transport"
    ENTERTAINMENT = "Entertainment"
    SHOPPING = "Shopping"
    UTILITIES = "Utilities"
    HEALTH = "Health"
    OTHER = "Other"

class Expense(BaseModel):
    """Internal model — includes user_id for DB operations."""
    id: Optional[str] = None
    user_id: str = Field(..., description="Firebase UID of the expense owner")
    amount: float = Field(..., gt=0, description="The cost of the expense")
    category: ExpenseCategory = Field(..., description="Category of the expense (e.g., Food, Transport)", min_length=1, max_length=50)
    description: Optional[str] = Field(None, description="Detailed description of the expense")
    date: date_type = Field(..., description="Date of the expense")

class ExpenseCreate(BaseModel):
    """What the client sends — no id, no user_id."""
    amount: float = Field(..., gt=0, description="The cost of the expense")
    category: ExpenseCategory = Field(..., description="Category of the expense (e.g., Food, Transport)")
    description: Optional[str] = Field(None, description="Detailed description of the expense", min_length=1, max_length=50   )
    date: date_type = Field(..., description="Date of the expense")

    @field_validator("date")
    @classmethod
    def date_not_in_future(cls, v: date_type) -> date_type:
        if v > date_type.today():
            raise ValueError("Expense date cannot be in the future")
        return v

class ExpenseResponse(BaseModel):
    """What the client receives — never exposes user_id."""
    id: str
    amount: float
    category: ExpenseCategory
    description: Optional[str] = None
    date: date_type

