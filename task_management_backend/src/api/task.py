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

from fastapi import HTTPException
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from src.api.db import Task, User
from datetime import datetime

def task_to_read(task: Task) -> TaskRead:
    return TaskRead(
        id=task.id,
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        status=task.status,
        creator_id=task.creator_id,
        assignee_id=task.assignee_id,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )

# PUBLIC_INTERFACE
@router.post(
    "/",
    summary="Create a new task",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED
)
async def create_task(
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Create a new task, assign to assignee_id if provided, creator_id required for real apps.
    Here, placeholder: use creator_id=1 for demonstration.
    """
    creator_id = 1  # For demo only; should be inferred from auth user!
    new_task = Task(
        title=task_in.title,
        description=task_in.description,
        due_date=task_in.due_date,
        status=task_in.status or "todo",
        creator_id=creator_id,
        assignee_id=task_in.assignee_id,
    )
    db.add(new_task)
    try:
        await db.commit()
        await db.refresh(new_task)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not create task: integrity error.")
    return task_to_read(new_task)

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
    db: AsyncSession = Depends(get_db_session),
):
    """
    List all tasks with optional filtering: by status, assignee_id, due_before.
    """
    filters = []
    if status:
        filters.append(Task.status == status)
    if assignee_id is not None:
        filters.append(Task.assignee_id == assignee_id)
    if due_before is not None:
        filters.append(Task.due_date != None)
        filters.append(Task.due_date <= due_before)
    query = select(Task)
    if filters:
        query = query.where(and_(*filters))
    result = await db.execute(query)
    tasks = result.scalars().all()
    return TaskListResponse(tasks=[task_to_read(t) for t in tasks], total=len(tasks))

# PUBLIC_INTERFACE
@router.get(
    "/{task_id}",
    summary="Get task by id",
    response_model=TaskRead
)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get a single task by id.
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return task_to_read(task)

# PUBLIC_INTERFACE
@router.put(
    "/{task_id}",
    summary="Update a task",
    response_model=TaskRead
)
async def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Update task fields by id. Only updates provided fields.
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    for attr, value in task_in.model_dump(exclude_unset=True).items():
        setattr(task, attr, value)
    try:
        await db.commit()
        await db.refresh(task)
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not update task.")
    return task_to_read(task)

# PUBLIC_INTERFACE
@router.delete(
    "/{task_id}",
    summary="Delete a task",
    response_model=MessageResponse
)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Delete a task by id.
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Unable to delete task.")
    return MessageResponse(message="Task deleted.")

# PUBLIC_INTERFACE
@router.post(
    "/{task_id}/assign",
    summary="Assign task to a user",
    response_model=TaskRead
)
async def assign_task(
    task_id: int,
    assignee_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Assign a task to the provided user ID.
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    # Validate assignee exists
    user_result = await db.execute(select(User).where(User.id == assignee_id))
    assignee = user_result.scalar_one_or_none()
    if not assignee:
        raise HTTPException(status_code=404, detail="Assignee user not found.")

    task.assignee_id = assignee_id
    try:
        await db.commit()
        await db.refresh(task)
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Failed to assign task.")
    return task_to_read(task)

# PUBLIC_INTERFACE
@router.post(
    "/{task_id}/status",
    summary="Update status of a task",
    response_model=TaskRead
)
async def update_status(
    task_id: int,
    new_status: str,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Update the status field (todo|in_progress|done) of a task.
    """
    if new_status not in ("todo", "in_progress", "done"):
        raise HTTPException(status_code=400, detail="Invalid status value.")
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    task.status = new_status
    try:
        await db.commit()
        await db.refresh(task)
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Failed to update status.")
    return task_to_read(task)

# PUBLIC_INTERFACE
@router.get(
    "/due/today",
    summary="Get tasks due today",
    response_model=TaskListResponse
)
async def get_due_today(
    db: AsyncSession = Depends(get_db_session),
):
    """
    Return a list of tasks due today.
    """
    today = datetime.utcnow().date()
    result = await db.execute(
        select(Task).where(Task.due_date == today)
    )
    tasks = result.scalars().all()
    return TaskListResponse(tasks=[task_to_read(t) for t in tasks], total=len(tasks))
