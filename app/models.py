from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date

class Order(SQLModel, table=True):
    """Procurement order table."""
    id: Optional[int] = Field(default=None, primary_key=True)
    vendor: str = Field(index=True)
    amount: float
    category: str  # e.g., "inventory", "rent", "utilities"
    date: date     # Uses Python's native `date` type
    status: str = Field(default="pending")  # "pending", "completed", "cancelled"

class Budget(SQLModel, table=True):
    """Budget tracking table."""
    id: Optional[int] = Field(default=None, primary_key=True)
    category: str = Field(unique=True, index=True)
    limit: float
    current_spending: float = Field(default=0.0)