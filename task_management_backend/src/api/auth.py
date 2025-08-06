from fastapi import APIRouter, Depends
from src.api.models import UserSignup, UserLogin, TokenResponse, UserRead
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.db import get_db_session

router = APIRouter(prefix="/auth", tags=["Authentication"])

# All in-memory user storage is removed. DB session is required for all endpoints.

from fastapi import HTTPException, status
from sqlalchemy import select
from src.api.db import User
from sqlalchemy.exc import IntegrityError

import hashlib

def hash_password(password: str) -> str:
    # For demonstration only; use a secure hash + salt (e.g. Argon2/bcrypt) in real apps!
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed: str) -> bool:
    return hash_password(plain_password) == hashed

# PUBLIC_INTERFACE
@router.post(
    "/signup",
    summary="Sign up a new user",
    response_model=UserRead,
    responses={201: {"description": "User created"}},
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    user_in: UserSignup,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Create a new user account. Checks uniqueness, hashes password.
    """
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered.")
    new_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hash_password(user_in.password),
        is_active=True,
    )
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Email already in use.")
    return UserRead(
        id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        is_active=new_user.is_active
    )

# PUBLIC_INTERFACE
@router.post(
    "/login",
    summary="User login",
    response_model=TokenResponse,
    responses={200: {"description": "User logged in"}, 401: {"description": "Invalid credentials"}},
)
async def login(
    login_in: UserLogin,
    db: AsyncSession = Depends(get_db_session),
):
    """
    User login to receive a (FAKE) bearer token after authenticating with the DB.
    """
    result = await db.execute(select(User).where(User.email == login_in.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    # Real token logic would be here (JWT, OAuth, etc.)
    return TokenResponse(access_token=f"fake-token-for-user-{user.id}", token_type="bearer")

# PUBLIC_INTERFACE
@router.get(
    "/me",
    summary="Get current authenticated user info",
    response_model=UserRead,
    responses={200: {"description": "Current user info"}}
)
async def get_me(
    token: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Retrieves info for the current user from token (FAKE token logic).
    In real world, parse the JWT token for ID. Here, use the fake pattern 'fake-token-for-user-{id}'
    """
    if not token or not token.startswith("fake-token-for-user-"):
        raise HTTPException(status_code=401, detail="Invalid/missing token")
    try:
        user_id = int(token.replace("fake-token-for-user-", "").split(":")[0])
    except Exception:
        raise HTTPException(status_code=401, detail="Malformed token")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return UserRead(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active
    )
