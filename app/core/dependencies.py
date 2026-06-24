"""
FastAPI Dependencies
=====================
Reusable dependencies injected into protected route handlers.
Validates the JWT Bearer token and returns the current authenticated user.
"""

import logging
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth_service import decode_access_token, get_user_by_username
from app.models.user import User

logger = logging.getLogger(__name__)

_bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency that extracts and validates the JWT Bearer token.

    Raises HTTP 401 if the token is missing, expired, or invalid.
    Raises HTTP 403 if the associated user account is inactive.

    Returns:
        The authenticated User ORM object.
    """
    token = credentials.credentials
    username = decode_access_token(token)

    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_username(db, username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive.",
        )

    return user
