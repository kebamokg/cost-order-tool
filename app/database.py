import os
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

# Database Configuration - Supports both SQLite (development) and PostgreSQL (production)
def get_database_url():
    """Determine database URL based on environment"""
    if "RENDER" in os.environ:
        # PostgreSQL for production (Render) - use direct connection string format
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        db_name = os.getenv("DB_NAME", "procurement")
        
        return f"postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}"
    else:
        # SQLite for development
        sqlite_file_name = "procurement.db"
        return f"sqlite:///{sqlite_file_name}"

# Get database URL
database_url = get_database_url()

# Set connection arguments based on database type
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

# Create database engine
engine = create_engine(database_url, connect_args=connect_args, echo=True)

def create_db_and_tables():
    """Create all database tables defined in SQLModel models."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency for FastAPI endpoints to get a database session."""
    with Session(engine) as session:
        yield session

# Type annotation for FastAPI dependency injection
SessionDep = Annotated[Session, Depends(get_session)]