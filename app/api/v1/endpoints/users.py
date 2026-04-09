import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import (
    get_current_active_user,
    require_admin,
    require_user_or_admin,
)
from app.core.exceptions import ForbiddenException
from app.db.session import get_db
from app.models.user import User
from app.schemas.response import APIResponse
from app.schemas.user import PasswordChange, UserRegister, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    summary="Get current user profile",
)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Returns the profile of the currently authenticated user."""
    return APIResponse.ok(UserResponse.model_validate(current_user))


@router.patch(
    "/me",
    response_model=APIResponse[UserResponse],
    summary="Update current user profile",
)
async def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    svc = UserService(db)
    user = await svc.update(current_user, payload)
    return APIResponse.ok(UserResponse.model_validate(user), "Profile updated.")


@router.post(
    "/me/change-password",
    response_model=APIResponse[None],
    summary="Change current user password",
)
async def change_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    svc = UserService(db)
    await svc.change_password(current_user, payload.current_password, payload.new_password)
    return APIResponse.ok(message="Password changed successfully.")


@router.delete(
    "/me",
    response_model=APIResponse[None],
    summary="Deactivate current account",
)
async def deactivate_me(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    svc = UserService(db)
    await svc.deactivate(current_user)
    return APIResponse.ok(message="Account deactivated.")


# ── Admin-only endpoints ──────────────────────────────────────────────────────

@router.get(
    "/{user_id}",
    response_model=APIResponse[UserResponse],
    summary="[Admin] Get user by ID",
)
async def get_user(
    user_id: uuid.UUID,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    svc = UserService(db)
    user = await svc.get_by_id(user_id)
    return APIResponse.ok(UserResponse.model_validate(user))


@router.post(
    "/",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="[Admin] Create a user with any role",
)
async def admin_create_user(
    payload: UserRegister,
    role: str = "user",
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    svc = UserService(db)
    user = await svc.create(payload, role=role)
    return APIResponse.ok(UserResponse.model_validate(user), "User created.")
