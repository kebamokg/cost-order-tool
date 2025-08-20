import os
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.engine import URL

# Database Configuration - Supports both SQLite (development) and PostgreSQL (production)
def get_database_url():
    """Determine database URL based on environment"""
    if "RENDER" in os.environ:
        # PostgreSQL for production (Render)
        return URL.create(
            drivername="postgresql",
            username=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME", "procurement"),
            port=5432
        )
    else:
        # SQLite for development
        sqlite_file_name = "procurement.db"
        return f"sqlite:///{sqlite_file_name}"

# Create engine with appropriate configuration
database_url = get_database_url()

if "sqlite" in str(database_url).lower():
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

# Create engine (moved outside if/else for consistency)
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