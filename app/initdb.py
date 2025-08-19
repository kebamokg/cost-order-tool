# init_db.py
from sqlmodel import SQLModel, create_engine
from models import Order, Budget
from datetime import date

# Create database and tables
sqlite_url = "sqlite:///procurement.db"
engine = create_engine(sqlite_url, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)
    
    # Pre-populate with test data
    with Session(engine) as session:
        # Add sample budgets
        budgets = [
            Budget(category="inventory", limit=10000.0),
            Budget(category="rent", limit=5000.0),
        ]
        session.add_all(budgets)
        
        # Add sample orders
        orders = [
            Order(vendor="Supplier A", amount=2000.0, category="inventory", date=date(2025, 8, 1)),
            Order(vendor="Supplier B", amount=1500.0, category="rent", date=date(2025, 8, 5)),
        ]
        session.add_all(orders)
        
        session.commit()

if __name__ == "__main__":
    init_db()
    print("Database created with sample data!")