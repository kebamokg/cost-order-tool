import os
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

def get_database_url():
    """Determine database URL based on environment"""
    if "RENDER" in os.environ:
        # Use individual environment variables (was working before)
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        db_name = os.getenv("DB_NAME")
        
        if all([db_user, db_password, db_host, db_name]):
            return f"postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}"
        else:
            print("ERROR: Missing database environment variables")
            return None
    else:
        # SQLite for development
        return "sqlite:///procurement.db"

# Get database URL
database_url = get_database_url()

# Debug print
print(f"DEBUG: Database URL = {database_url}")

# Set connection arguments
connect_args = {}
if database_url and database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Create database engine
if database_url:
    engine = create_engine(database_url, connect_args=connect_args, echo=True)
    print("DEBUG: Database engine created successfully")
else:
    engine = None
    print("ERROR: No database URL configured")

def create_db_and_tables():
    """Create all database tables defined in SQLModel models."""
    if engine:
        SQLModel.metadata.create_all(engine)
        print("DEBUG: Database tables created successfully")
    else:
        print("ERROR: Cannot create tables - no database engine")

def get_session():
    """Dependency for FastAPI endpoints to get a database session."""
    if engine:
        with Session(engine) as session:
            yield session
    else:
        raise Exception("Database not configured")

# Type annotation for FastAPI dependency injection
SessionDep = Annotated[Session, Depends(get_session)]