"""
Authentication Service
=======================
Handles password hashing, JWT token generation and validation,
and user lookup helpers used by the auth routes and dependencies.

JWT tokens are signed with a secret key stored in the .env file.
Passwords are hashed using bcrypt via passlib.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.user import User

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration — read from environment variables
# ---------------------------------------------------------------------------
_SECRET_KEY   = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
_ALGORITHM    = "HS256"
_TOKEN_EXPIRE = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

# Bcrypt password hashing context
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------------------------
# Password utilities
# ---------------------------------------------------------------------------

def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if the plaintext password matches the stored hash."""
    return _pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------------------------
# JWT utilities
# ---------------------------------------------------------------------------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate a signed JWT access token.

    Args:
        data:          Payload to encode (typically {"sub": username}).
        expires_delta: Custom expiry duration. Defaults to JWT_EXPIRE_MINUTES.

    Returns:
        Encoded JWT string.
    """
    payload = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=_TOKEN_EXPIRE))
    payload["exp"] = expire
    return jwt.encode(payload, _SECRET_KEY, algorithm=_ALGORITHM)


def decode_access_token(token: str) -> Optional[str]:
    """
    Decode and validate a JWT token.

    Args:
        token: Encoded JWT string.

    Returns:
        The username (sub claim) if the token is valid, else None.
    """
    try:
        payload = jwt.decode(token, _SECRET_KEY, algorithms=[_ALGORITHM])
        username: Optional[str] = payload.get("sub")
        return username
    except JWTError:
        return None


# ---------------------------------------------------------------------------
# User helpers
# ---------------------------------------------------------------------------

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Fetch a user record by username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Fetch a user record by email address."""
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Validate credentials and return the User object if correct.

    Args:
        db:       Active database session.
        username: Submitted username.
        password: Submitted plaintext password.

    Returns:
        User object if authentication succeeds, else None.
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


def create_user(db: Session, username: str, email: str, password: str) -> User:
    """
    Register a new user in the database.

    Args:
        db:       Active database session.
        username: Desired username (must be unique).
        email:    Email address (must be unique).
        password: Plaintext password (will be hashed before storage).

    Returns:
        The newly created User object.
    """
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("New user registered: %s", username)
    return user
