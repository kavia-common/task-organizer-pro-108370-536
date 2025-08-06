import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime, Text, ForeignKey, func
)
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

DB_URL = os.getenv('POSTGRES_URL')

if not DB_URL:
    raise RuntimeError("POSTGRES_URL environment variable is not set.")

# Async engine for SQLAlchemy
engine = create_async_engine(DB_URL, pool_pre_ping=True)

# Async session factory for FastAPI dependency injection
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""
    pass


# ORM models

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    # Tasks assigned to this user
    assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="[Task.assignee_id]")
    # Tasks created by this user
    created_tasks = relationship("Task", back_populates="creator", foreign_keys="[Task.creator_id]")


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(Date, nullable=True)
    status = Column(String(32), default='todo', nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    creator = relationship(
        "User",
        back_populates="created_tasks",
        foreign_keys=[creator_id]
    )
    assignee = relationship(
        "User",
        back_populates="assigned_tasks",
        foreign_keys=[assignee_id]
    )


# Database init and session handling

# PUBLIC_INTERFACE
async def get_db_session():
    """Provide an async SQLAlchemy session for each request (FastAPI dependency)."""
    async with async_session() as session:
        yield session

# PUBLIC_INTERFACE
async def init_db():
    """Initialize database tables for the first time (should be run on app startup or via alembic migrations)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
