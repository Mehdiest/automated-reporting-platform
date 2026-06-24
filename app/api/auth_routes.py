"""
Authentication Routes
======================
REST endpoints for user registration, login, and profile retrieval.

POST /auth/register — Create a new user account
POST /auth/login    — Authenticate and receive a JWT token
GET  /auth/me       — Return the current authenticated user's profile
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.auth_service import (
    authenticate_user,
    create_user,
    create_access_token,
    get_user_by_username,
    get_user_by_email,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    """Payload for creating a new user account."""
    username: str  = Field(..., min_length=3, max_length=64, example="mehdi")
    email:    EmailStr = Field(..., example="mehdi@example.com")
    password: str  = Field(..., min_length=6, example="securepassword")


class LoginRequest(BaseModel):
    """Payload for authenticating an existing user."""
    username: str = Field(..., example="mehdi")
    password: str = Field(..., example="securepassword")


class TokenResponse(BaseModel):
    """JWT token returned after successful login."""
    access_token: str
    token_type:   str = "bearer"


class UserResponse(BaseModel):
    """Public profile of the authenticated user."""
    id:         int
    username:   str
    email:      str
    is_active:  bool

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> User:
    """
    Register a new user account.

    Returns 400 if the username or email is already taken.
    """
    if get_user_by_username(db, payload.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{payload.username}' is already taken.",
        )

    if get_user_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{payload.email}' is already registered.",
        )

    return create_user(db, payload.username, payload.email, payload.password)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> dict:
    """
    Authenticate a user and return a JWT Bearer token.

    Returns 401 if credentials are invalid or account is inactive.
    """
    user = authenticate_user(db, payload.username, payload.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    """
    Return the profile of the currently authenticated user.

    Requires a valid JWT Bearer token in the Authorization header.
    """
    return current_user
