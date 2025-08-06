from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional, Dict
from datetime import datetime, date
from src.api.models import (
    TaskCreate,
    TaskUpdate,
    TaskRead,
    TaskListResponse,
    MessageResponse,
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# FAKE in-memory storage
_fake_task_db: Dict[int, Dict] = {}
_initial_task_id = 1

def _create_fake_task_id():
    global _initial_task_id
    xid = _initial_task_id
    _initial_task_id += 1
    return xid

# PUBLIC_INTERFACE
@router.post(
    "/",
    summary="Create a new task",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED
)
def create_task(task_in: TaskCreate):
    """Create a new task. (in-memory only, for demo purpose)"""
    task_id = _create_fake_task_id()
    now = datetime.utcnow()
    data = {
        "id": task_id,
        "title": task_in.title,
        "description": task_in.description or "",
        "due_date": task_in.due_date,
        "status": task_in.status,
        "creator_id": 1,  # Demo static creator
        "assignee_id": task_in.assignee_id,
        "created_at": now,
        "updated_at": now,
    }
    _fake_task_db[task_id] = data
    return TaskRead(**data)

# PUBLIC_INTERFACE
@router.get(
    "/",
    summary="List tasks (all or filtered)",
    response_model=TaskListResponse
)
def list_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee id"),
    due_before: Optional[date] = Query(None, description="Tasks due before this date")
):
    """List all tasks with optional filtering."""
    filtered = list(_fake_task_db.values())
    if status:
        filtered = [t for t in filtered if t["status"] == status]
    if assignee_id:
        filtered = [t for t in filtered if t["assignee_id"] == assignee_id]
    if due_before:
        filtered = [t for t in filtered if t["due_date"] and t["due_date"] < due_before]
    return TaskListResponse(tasks=[TaskRead(**task) for task in filtered], total=len(filtered))

# PUBLIC_INTERFACE
@router.get(
    "/{task_id}",
    summary="Get task by id",
    response_model=TaskRead
)
def get_task(task_id: int):
    """Get a single task by id."""
    task = _fake_task_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskRead(**task)

# PUBLIC_INTERFACE
@router.put(
    "/{task_id}",
    summary="Update a task",
    response_model=TaskRead
)
def update_task(task_id: int, task_in: TaskUpdate):
    """Update task fields by id."""
    task = _fake_task_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for field, value in task_in.dict(exclude_unset=True).items():
        if value is not None:
            task[field] = value
    task["updated_at"] = datetime.utcnow()
    return TaskRead(**task)

# PUBLIC_INTERFACE
@router.delete(
    "/{task_id}",
    summary="Delete a task",
    response_model=MessageResponse
)
def delete_task(task_id: int):
    """Delete a task by id."""
    if task_id not in _fake_task_db:
        raise HTTPException(status_code=404, detail="Task not found")
    del _fake_task_db[task_id]
    return MessageResponse(message="Task deleted successfully.")

# PUBLIC_INTERFACE
@router.post(
    "/{task_id}/assign",
    summary="Assign task to a user",
    response_model=TaskRead
)
def assign_task(task_id: int, assignee_id: int):
    """Assign a task to a user (placeholder logic)"""
    task = _fake_task_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task["assignee_id"] = assignee_id
    task["updated_at"] = datetime.utcnow()
    return TaskRead(**task)

# PUBLIC_INTERFACE
@router.post(
    "/{task_id}/status",
    summary="Update status of a task",
    response_model=TaskRead
)
def update_status(task_id: int, new_status: str):
    """Update the status field (todo|in_progress|done) of a task."""
    task = _fake_task_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task["status"] = new_status
    task["updated_at"] = datetime.utcnow()
    return TaskRead(**task)

# PUBLIC_INTERFACE
@router.get(
    "/due/today",
    summary="Get tasks due today",
    response_model=TaskListResponse
)
def get_due_today():
    """Return a list of tasks due today (due date reminders placeholder)."""
    today = datetime.utcnow().date()
    due_tasks = [t for t in _fake_task_db.values() if t["due_date"] == today]
    return TaskListResponse(tasks=[TaskRead(**task) for task in due_tasks], total=len(due_tasks))
