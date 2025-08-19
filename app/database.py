from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine, Field

# Database Configuration
sqlite_file_name = "procurement.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args, echo=True)  # `echo=True` logs SQL queries (debug)

def create_db_and_tables():
    """Create all database tables defined in SQLModel models."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency for FastAPI endpoints to get a database session."""
    with Session(engine) as session:
        yield session

# Type annotation for FastAPI dependency injection
SessionDep = Annotated[Session, Depends(get_session)]