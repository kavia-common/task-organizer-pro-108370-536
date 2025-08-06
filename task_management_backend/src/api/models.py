from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date

# User models

# PUBLIC_INTERFACE
class UserSignup(BaseModel):
    """Schema for a new user signup request."""
    email: EmailStr = Field(..., description="User email address (unique)")
    password: str = Field(..., min_length=6, description="User password (hashed in actual implementation)")
    full_name: Optional[str] = Field(None, description="Full name of the user")

# PUBLIC_INTERFACE
class UserLogin(BaseModel):
    """Schema for user login requests."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password")

# PUBLIC_INTERFACE
class UserRead(BaseModel):
    """Response schema for user data."""
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool

# Auth/token models

# PUBLIC_INTERFACE
class TokenResponse(BaseModel):
    """Response schema for login/token requests."""
    access_token: str
    token_type: str = "bearer"

# Task models

class TaskBase(BaseModel):
    """Base schema for a task (shared props)."""
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = Field(None, description="Task due date (reminder placeholder)")
    status: str = Field("todo", description="Current status (todo|in_progress|done)")

# PUBLIC_INTERFACE
class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    assignee_id: Optional[int] = Field(None, description="ID of assigned user (optional for creation)")

# PUBLIC_INTERFACE
class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[str] = None
    assignee_id: Optional[int] = None

# PUBLIC_INTERFACE
class TaskRead(TaskBase):
    """Schema for returning a task."""
    id: int
    creator_id: int
    assignee_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

# PUBLIC_INTERFACE
class TaskListResponse(BaseModel):
    """Response schema for a list of tasks."""
    tasks: List[TaskRead]
    total: int

# PUBLIC_INTERFACE
class MessageResponse(BaseModel):
    """Generic response with a message."""
    message: str

