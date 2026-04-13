from pydantic import BaseModel, Field
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
    id: Optional[int] = None
    user_id: str = Field(..., description="Firebase UID of the expense owner")
    amount: float = Field(..., gt=0, description="The cost of the expense")
    category: ExpenseCategory = Field(..., description="Category of the expense (e.g., Food, Transport)")
    description: Optional[str] = Field(None, description="Detailed description of the expense")
    date: date_type = Field(..., description="Date of the expense")
