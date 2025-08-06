from fastapi import APIRouter, Depends
from src.api.models import UserSignup, UserLogin, TokenResponse, UserRead
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.db import get_db_session

router = APIRouter(prefix="/auth", tags=["Authentication"])

# All in-memory user storage is removed. DB session is required for all endpoints.

# PUBLIC_INTERFACE
@router.post(
    "/signup",
    summary="Sign up a new user",
    response_model=UserRead,
    responses={201: {"description": "User created"}},
)
async def signup(
    user_in: UserSignup,
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new user account (DB-backed, implementation pending)."""
    raise NotImplementedError("DB logic not yet implemented.")

# PUBLIC_INTERFACE
@router.post(
    "/login",
    summary="User login",
    response_model=TokenResponse,
    responses={200: {"description": "User logged in"}, 401: {"description": "Invalid credentials"}},
)
async def login(
    login_in: UserLogin,
    db: AsyncSession = Depends(get_db_session)
):
    """User login to receive bearer token (DB-backed, implementation pending)."""
    raise NotImplementedError("DB logic not yet implemented.")

# PUBLIC_INTERFACE
@router.get(
    "/me",
    summary="Get current authenticated user info",
    response_model=UserRead,
    responses={200: {"description": "Current user info"}}
)
async def get_me(
    token: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session)
):
    """Get info about the currently authenticated user (DB-backed, implementation pending)."""
    raise NotImplementedError("DB logic not yet implemented.")

