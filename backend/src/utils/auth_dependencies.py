"""FastAPI dependencies for authentication."""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.connection import get_db
from src.db.repositories.user_repo import UserRepository
from src.services.auth_service import auth_service
from src.models.user import User

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: Bearer token from Authorization header
        db: Database session

    Returns:
        Current user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Extract token
    token = credentials.credentials

    # Decode token and get user ID
    user_id = auth_service.get_user_id_from_token(token)

    # Get user from database
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_id(user_id, load_profile=True)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.

    Useful for endpoints that work for both authenticated and anonymous users.

    Args:
        credentials: Optional bearer token
        db: Database session

    Returns:
        Current user or None
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        user_id = auth_service.get_user_id_from_token(token)

        user_repo = UserRepository(db)
        user = await user_repo.get_user_by_id(user_id, load_profile=True)

        if user and user.is_active:
            return user
    except HTTPException:
        pass

    return None
