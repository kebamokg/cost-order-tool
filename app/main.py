from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from .database import engine, SessionDep, create_db_and_tables
from .models import Order, Budget
from datetime import date

app = FastAPI()

# Initialize database tables on startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

class BudgetWithAlert(BaseModel):
    """Response model that includes alert status"""
    id: int
    category: str
    limit: float
    current_spending: float
    alert: Optional[Dict[str, Any]] = None

def check_budget_alerts(budget: Budget) -> Optional[Dict[str, Any]]:
    """Check if budget is nearing or exceeding limits"""
    spending_ratio = budget.current_spending / budget.limit
    
    if spending_ratio >= 1:
        return {
            "level": "danger",
            "message": f"ALERT: Budget for '{budget.category}' EXCEEDED! (Current: {budget.current_spending}/{budget.limit})"
        }
    elif spending_ratio >= 0.8:
        return {
            "level": "warning",
            "message": f"WARNING: Budget for '{budget.category}' is 80% used! (Current: {budget.current_spending}/{budget.limit})"
        }
    return None

# ===== DATABASE INITIALIZATION ENDPOINT =====
@app.post("/init-db")
def initialize_database():
    """Initialize database tables (for first-time setup on Render)"""
    try:
        create_db_and_tables()
        return {"message": "Database tables created successfully", "status": "success"}
    except Exception as e:
        return {"message": f"Database initialization failed: {str(e)}", "status": "error"}

# ===== ORDER ENDPOINTS =====
@app.post("/orders/", response_model=Order)
def create_order(order: Order, session: SessionDep):
    """Create a new procurement order"""
    order.date = date.fromisoformat(order.date)
    session.add(order)
    session.commit()
    session.refresh(order)
    
    # Update budget spending and check alerts
    budget = session.exec(select(Budget).where(Budget.category == order.category)).first()
    if budget:
        budget.current_spending += order.amount
        session.add(budget)
        session.commit()
        alert = check_budget_alerts(budget)
        if alert:
            color_code = "\033[91m" if alert["level"] == "danger" else "\033[93m"
            print(color_code + alert["message"] + "\033[0m")
    
    return order

@app.get("/orders/", response_model=List[Order])
def read_orders(session: SessionDep, skip: int = 0, limit: int = 100):
    """List all orders with pagination"""
    return session.exec(select(Order).offset(skip).limit(limit)).all()

@app.get("/orders/{order_id}", response_model=Order)
def read_order(order_id: int, session: SessionDep):
    """Get a specific order by ID"""
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# ===== BUDGET ENDPOINTS =====
@app.post("/budgets/", response_model=Budget)
def create_budget(budget: Budget, session: SessionDep):
    """Create a new budget category"""
    existing = session.exec(select(Budget).where(Budget.category == budget.category)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Budget for this category already exists")
    
    session.add(budget)
    session.commit()
    session.refresh(budget)
    return budget

@app.get("/budgets/", response_model=List[BudgetWithAlert])
def read_budgets(session: SessionDep, skip: int = 0, limit: int = 100):
    """List all budgets with pagination"""
    budgets = session.exec(select(Budget).offset(skip).limit(limit)).all()
    return [{
        "id": b.id,
        "category": b.category,
        "limit": b.limit,
        "current_spending": b.current_spending,
        "alert": check_budget_alerts(b)
    } for b in budgets]

@app.get("/budgets/{category}", response_model=BudgetWithAlert)
def read_budget(category: str, session: SessionDep):
    """Get budget details by category"""
    budget = session.exec(select(Budget).where(Budget.category == category)).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    return {
        "id": budget.id,
        "category": budget.category,
        "limit": budget.limit,
        "current_spending": budget.current_spending,
        "alert": check_budget_alerts(budget)
    }

@app.delete("/budgets/{category}")
def delete_budget(category: str, session: SessionDep):
    budget = session.exec(select(Budget).where(Budget.category == category)).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    session.delete(budget)
    session.commit()
    return {"message": "Budget deleted"}

@app.patch("/budgets/{category}/spending")
def update_spending(category: str, amount: float, session: SessionDep):
    """Manually adjust spending"""
    budget = session.exec(select(Budget).where(Budget.category == category)).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    budget.current_spending += amount
    session.add(budget)
    session.commit()
    
    alert = check_budget_alerts(budget)
    if alert:
        color_code = "\033[91m" if alert["level"] == "danger" else "\033[93m"
        print(color_code + alert["message"] + "\033[0m")
    
    return {"message": "Spending updated", "alert": alert}