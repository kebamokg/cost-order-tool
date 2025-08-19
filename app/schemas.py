from pydantic import BaseModel
from typing import Optional

class OrderCreate(BaseModel):
    vendor: str
    amount: float
    category: str
    date: str
    status: str = "pending"

class OrderResponse(OrderCreate):
    id: int

class BudgetCreate(BaseModel):
    category: str
    limit: float

class BudgetResponse(BudgetCreate):
    current_spending: float