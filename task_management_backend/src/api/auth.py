from fastapi import APIRouter, HTTPException
from src.api.models import UserSignup, UserLogin, TokenResponse, UserRead
from typing import Dict, Optional

router = APIRouter(prefix="/auth", tags=["Authentication"])

# FAKE db in-memory placeholder for demonstration
fake_users_db: Dict[str, Dict] = {}

# PUBLIC_INTERFACE
@router.post(
    "/signup",
    summary="Sign up a new user",
    response_model=UserRead,
    responses={201: {"description": "User created"}},
)
def signup(user_in: UserSignup):
    """Create a new user account.
    ---
    - **email**: unique string
    - **password**: string
    """
    if user_in.email in fake_users_db:
        raise HTTPException(status_code=400, detail="Email already exists.")
    new_user = {
        "id": len(fake_users_db) + 1,
        "email": user_in.email,
        "full_name": user_in.full_name,
        "is_active": True,
        "hashed_password": f"not-really-{user_in.password}-hashed"  # PLACEHOLDER
    }
    fake_users_db[user_in.email] = new_user
    return UserRead(id=new_user["id"], email=new_user["email"], full_name=new_user["full_name"], is_active=new_user["is_active"])

# PUBLIC_INTERFACE
@router.post(
    "/login",
    summary="User login",
    response_model=TokenResponse,
    responses={200: {"description": "User logged in"}, 401: {"description": "Invalid credentials"}},
)
def login(login_in: UserLogin):
    """User login to receive bearer token (FAKE implementation)."""
    user = fake_users_db.get(login_in.email)
    if user is None or user["hashed_password"] != f"not-really-{login_in.password}-hashed":
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # In a real app, generate a secure JWT token linked to the user id, exp, etc.
    fake_token = f"fake-token-for-{login_in.email}"
    return TokenResponse(access_token=fake_token)

# PUBLIC_INTERFACE
@router.get(
    "/me",
    summary="Get current authenticated user info",
    response_model=UserRead,
    responses={200: {"description": "Current user info"}}
)
def get_me(token: Optional[str] = None):
    """Get info about the currently authenticated user (FAKE token, placeholder logic)."""
    # Just return the first user for demonstration
    if not fake_users_db:
        raise HTTPException(status_code=401, detail="No authenticated user.")
    first_email = list(fake_users_db.keys())[0]
    user = fake_users_db[first_email]
    return UserRead(id=user["id"], email=user["email"], full_name=user["full_name"], is_active=user["is_active"])

