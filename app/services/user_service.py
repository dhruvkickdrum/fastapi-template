import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.core.logging import get_logger
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserRegister, UserUpdate

logger = get_logger(__name__)


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> User:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundException(f"User {user_id} not found.")
        return user

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def create(self, data: UserRegister, role: str = "user") -> User:
        existing = await self.get_by_email(data.email)
        if existing:
            raise ConflictException("A user with this email already exists.")

        user = User(
            email=data.email.lower(),
            full_name=data.full_name,
            password_hash=hash_password(data.password),
            role=role,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        logger.info("User created: %s", user.email)
        return user

    async def update(self, user: User, data: UserUpdate) -> User:
        if data.email and data.email.lower() != user.email:
            existing = await self.get_by_email(data.email)
            if existing:
                raise ConflictException("Email already in use.")
            user.email = data.email.lower()

        if data.full_name is not None:
            user.full_name = data.full_name

        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def change_password(
        self, user: User, current_password: str, new_password: str
    ) -> User:
        if not verify_password(current_password, user.password_hash):
            from app.core.exceptions import BadRequestException
            raise BadRequestException("Current password is incorrect.")
        user.password_hash = hash_password(new_password)
        await self.db.flush()
        await self.db.refresh(user)
        logger.info("Password changed for user: %s", user.email)
        return user

    async def deactivate(self, user: User) -> User:
        user.is_active = False
        await self.db.flush()
        await self.db.refresh(user)
        logger.info("User deactivated: %s", user.email)
        return user
