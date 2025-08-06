from fastapi import APIRouter, Query, status, Depends
from typing import Optional
from datetime import date
from src.api.models import (
    TaskCreate,
    TaskUpdate,
    TaskRead,
    TaskListResponse,
    MessageResponse,
)
from src.api.db import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# NOTE: All "in-memory" logic removed. DB session is now required via Depends(get_db_session).
# Actual CRUD logic to be implemented in the next step.
# Here, we just provide placeholder skeletons for DB session use.

# PUBLIC_INTERFACE
@router.post(
    "/",
    summary="Create a new task",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED
)
async def create_task(
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new task (DB-backed, implementation pending)."""
    raise NotImplementedError("DB logic not yet implemented.")

# PUBLIC_INTERFACE
@router.get(
    "/",
    summary="List tasks (all or filtered)",
    response_model=TaskListResponse
)
async def list_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee id"),
    due_before: Optional[date] = Query(None, description="Tasks due before this date"),
    db: AsyncSession = Depends(get_db_session)
):
    """List all tasks with optional filtering (DB-backed, implementation pending)."""
    raise NotImplementedError("DB logic not yet implemented.")

# PUBLIC_INTERFACE
@router.get(
    "/{task_id}",
    summary="Get task by id",
    response_model=TaskRead
)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Get a single task by id (DB-backed, implementation pending)."""
    raise NotImplementedError("DB logic not yet implemented.")

# PUBLIC_INTERFACE
@router.put(
    "/{task_id}",
    summary="Update a task",
    response_model=TaskRead
)
async def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """Update task fields by id (DB-backed, implementation pending)."""
    raise NotImplementedError("DB logic not yet implemented.")

# PUBLIC_INTERFACE
@router.delete(
    "/{task_id}",
    summary="Delete a task",
    response_model=MessageResponse
)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Delete a task by id (DB-backed, implementation pending)."""
    raise NotImplementedError("DB logic not yet implemented.")

# PUBLIC_INTERFACE
@router.post(
    "/{task_id}/assign",
    summary="Assign task to a user",
    response_model=TaskRead
)
async def assign_task(
    task_id: int,
    assignee_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Assign a task to a user (DB-backed, implementation pending)."""
    raise NotImplementedError("DB logic not yet implemented.")

# PUBLIC_INTERFACE
@router.post(
    "/{task_id}/status",
    summary="Update status of a task",
    response_model=TaskRead
)
async def update_status(
    task_id: int,
    new_status: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Update the status field (todo|in_progress|done) of a task (DB-backed, implementation pending)."""
    raise NotImplementedError("DB logic not yet implemented.")

# PUBLIC_INTERFACE
@router.get(
    "/due/today",
    summary="Get tasks due today",
    response_model=TaskListResponse
)
async def get_due_today(
    db: AsyncSession = Depends(get_db_session)
):
    """Return a list of tasks due today (DB-backed, implementation pending)."""
    raise NotImplementedError("DB logic not yet implemented.")
