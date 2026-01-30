"""
JWT Authentication Utilities
Handles token creation, verification, and user authentication
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .config import settings
from models import get_db, User

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with issuer and audience claims.

    Args:
        data: Data to encode in the token (typically {"sub": user_id})
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({
        "exp": expire,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token with issuer and audience validation.

    Args:
        token: JWT token string

    Returns:
        Decoded payload dict if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER
        )
        return payload
    except JWTError:
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        token: JWT token from request header
        db: Database session

    Returns:
        User object if authenticated

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id_int).first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (checks is_active flag).

    Args:
        current_user: User from get_current_user dependency

    Returns:
        User object if active

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


# Optional dependency - returns None if not authenticated
async def get_optional_user(
    token: Optional[str] = Depends(
        OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login", auto_error=False)
    ),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if token provided, None otherwise.
    Useful for endpoints that work both authenticated and anonymously.

    Args:
        token: Optional JWT token
        db: Database session

    Returns:
        User object if authenticated, None otherwise
    """
    if token is None:
        return None

    payload = verify_token(token)
    if payload is None:
        return None

    user_id: str = payload.get("sub")
    if user_id is None:
        return None

    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        return None

    return db.query(User).filter(User.id == user_id_int).first()


async def get_current_user_or_demo(
    token: Optional[str] = Depends(
        OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login", auto_error=False)
    ),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user if authenticated, otherwise create/return demo user.
    Used in DEMO_MODE for testing without authentication.

    Args:
        token: Optional JWT token
        db: Database session

    Returns:
        User object (authenticated or demo user)
    """
    # Try to get authenticated user first
    if token:
        payload = verify_token(token)
        if payload:
            user_id: str = payload.get("sub")
            if user_id:
                try:
                    user_id_int = int(user_id)
                    user = db.query(User).filter(User.id == user_id_int).first()
                    if user:
                        return user
                except (ValueError, TypeError):
                    pass
    
    # If not authenticated and in demo mode, use/create demo user
    if settings.DEMO_MODE:
        demo_user = db.query(User).filter(User.username == "demo_user").first()
        if not demo_user:
            # Create demo user
            demo_user = User(
                email="demo@example.com",
                username="demo_user",
                hashed_password="demo_hash",  # Not used in demo mode
                is_active=True
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
        return demo_user
    
    # If not demo mode and no valid auth, raise error
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required (not in demo mode)",
        headers={"WWW-Authenticate": "Bearer"},
    )
