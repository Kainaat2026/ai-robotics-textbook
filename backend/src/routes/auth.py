"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.connection import get_db
from src.db.repositories.user_repo import UserRepository
from src.services.auth_service import auth_service
from src.models.auth import (
    UserSignupRequest,
    UserLoginRequest,
    QuestionnaireRequest,
    PasswordChangeRequest,
    AuthToken,
    UserMeResponse,
    UserProfileResponse
)
from src.models.user import User
from src.utils.auth_dependencies import get_current_user

router = APIRouter()


@router.post("/auth/signup", response_model=AuthToken, status_code=status.HTTP_201_CREATED)
async def signup(
    request: UserSignupRequest,
    db: AsyncSession = Depends(get_db)
) -> AuthToken:
    """
    Register a new user account.

    Args:
        request: Signup data (email, password)
        db: Database session

    Returns:
        JWT access token

    Raises:
        400: Email already registered or invalid password

    Example:
        POST /api/auth/signup
        {
            "email": "user@example.com",
            "password": "SecurePass123"
        }
    """
    user_repo = UserRepository(db)

    # Validate email format
    if not auth_service.validate_email(request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )

    # Validate password strength
    is_valid, error_msg = auth_service.validate_password_strength(request.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    # Check if email already exists
    existing_user = await user_repo.get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    password_hash = auth_service.hash_password(request.password)

    # Create user
    user = await user_repo.create_user(
        email=request.email,
        password_hash=password_hash
    )

    # Create default profile
    await user_repo.create_user_profile(user.id)

    # Generate JWT token
    access_token = auth_service.create_access_token(
        user_id=user.id,
        email=user.email
    )

    return AuthToken(access_token=access_token)


@router.post("/auth/login", response_model=AuthToken)
async def login(
    request: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
) -> AuthToken:
    """
    Login with email and password.

    Args:
        request: Login credentials
        db: Database session

    Returns:
        JWT access token

    Raises:
        401: Invalid credentials

    Example:
        POST /api/auth/login
        {
            "email": "user@example.com",
            "password": "SecurePass123"
        }
    """
    user_repo = UserRepository(db)

    # Get user by email
    user = await user_repo.get_user_by_email(request.email)

    if not user:
        # Use generic error message to prevent email enumeration
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not auth_service.verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Generate JWT token
    access_token = auth_service.create_access_token(
        user_id=user.id,
        email=user.email
    )

    return AuthToken(access_token=access_token)


@router.get("/auth/me", response_model=UserMeResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserMeResponse:
    """
    Get current authenticated user information.

    Requires: Bearer token in Authorization header

    Returns:
        Current user profile

    Example:
        GET /api/auth/me
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    # Convert profile to response model if exists
    profile_response = None
    if current_user.profile:
        profile_response = UserProfileResponse(
            python_level=current_user.profile.python_level,
            ai_experience=current_user.profile.ai_experience,
            robotics_experience=current_user.profile.robotics_experience,
            has_rtx_gpu=current_user.profile.has_rtx_gpu,
            preferred_language=current_user.profile.preferred_language
        )

    return UserMeResponse(
        id=current_user.id,
        email=current_user.email,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at.isoformat(),
        profile=profile_response
    )


@router.post("/auth/questionnaire", response_model=UserProfileResponse)
async def submit_questionnaire(
    request: QuestionnaireRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserProfileResponse:
    """
    Submit or update questionnaire (skill assessment).

    Requires: Authentication

    Args:
        request: Questionnaire data
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated user profile

    Example:
        POST /api/auth/questionnaire
        {
            "python_level": "advanced",
            "ai_experience": "intermediate",
            "robotics_experience": "beginner",
            "has_rtx_gpu": true,
            "preferred_language": "en"
        }
    """
    user_repo = UserRepository(db)

    # Update profile
    profile = await user_repo.update_user_profile(
        user_id=current_user.id,
        python_level=request.python_level,
        ai_experience=request.ai_experience,
        robotics_experience=request.robotics_experience,
        has_rtx_gpu=request.has_rtx_gpu,
        preferred_language=request.preferred_language
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )

    return UserProfileResponse.model_validate(profile)


@router.post("/auth/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change user password.

    Requires: Authentication

    Args:
        request: Current and new password
        current_user: Authenticated user
        db: Database session

    Returns:
        204 No Content

    Example:
        POST /api/auth/change-password
        {
            "current_password": "OldPass123",
            "new_password": "NewSecurePass456"
        }
    """
    # Verify current password
    if not auth_service.verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )

    # Validate new password strength
    is_valid, error_msg = auth_service.validate_password_strength(request.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    # Hash new password
    new_password_hash = auth_service.hash_password(request.new_password)

    # Update password
    user_repo = UserRepository(db)
    await user_repo.update_user(
        user_id=current_user.id,
        password_hash=new_password_hash
    )
