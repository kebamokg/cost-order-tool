import os
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

import sqlalchemy.dialects.postgresql

sqlalchemy.dialects.postgresql.psycopg2.dialect.driver = "psycopg"
os.environ['SQLALCHEMY_WARN_20'] = '1'
os.environ['SQLALCHEMY_SILENCE_UBER_WARNING'] = '1'

def get_database_url():
    """Determine database URL based on environment"""
    if "RENDER" in os.environ:
        # Use the connection string provided by Render
        database_url = os.getenv("DATABASE_URL")
        
        # Debug: Print the URL to check it's being read
        print(f"DEBUG: DATABASE_URL from env = {database_url}")
        
        # Convert postgres:// to postgresql:// for SQLAlchemy compatibility
        if database_url and database_url.startswith("postgres://"):
            converted_url = database_url.replace("postgres://", "postgresql://", 1)
            print(f"DEBUG: Converted URL = {converted_url}")
            return converted_url
        
        return database_url
    else:
        # SQLite for development
        return "sqlite:///procurement.db"

# Get database URL
database_url = get_database_url()

# Debug print
print(f"DEBUG: Final database_url = {database_url}")

# Set connection arguments based on database type
connect_args = {}
if database_url and database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Create database engine only if URL is valid
if database_url:
    engine = create_engine(database_url, connect_args=connect_args, echo=True)
    print("DEBUG: Database engine created successfully")
else:
    engine = None
    print("ERROR: database_url is None - check DATABASE_URL environment variable")

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
        raise Exception("Database not configured - check DATABASE_URL environment variable")

# Type annotation for FastAPI dependency injection
SessionDep = Annotated[Session, Depends(get_session)]