from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.response import APIResponse
from app.schemas.user import RefreshRequest, Token, UserLogin, UserRegister, UserResponse
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new account with email and a strong password.",
)
async def register(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    Register a new user account.

    - **email**: valid email address (must be unique)
    - **password**: min 8 chars, must include upper/lower/digit/special char
    - **full_name**: optional display name
    """
    svc = UserService(db)
    user = await svc.create(payload)
    return APIResponse.ok(UserResponse.model_validate(user), "User registered successfully.")


@router.post(
    "/login",
    response_model=APIResponse[Token],
    summary="Login and obtain JWT tokens",
)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticate with email and password. Returns access + refresh tokens.
    """
    svc = AuthService(db)
    token = await svc.login(payload)
    return APIResponse.ok(token, "Login successful.")


@router.post(
    "/refresh",
    response_model=APIResponse[Token],
    summary="Refresh access token",
)
async def refresh_token(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """
    Exchange a valid refresh token for a new access token pair.
    """
    svc = AuthService(db)
    token = await svc.refresh(payload.refresh_token)
    return APIResponse.ok(token, "Token refreshed.")
