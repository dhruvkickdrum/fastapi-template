from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models.user import User
from app.schemas.user import Token, UserLogin
from app.services.user_service import UserService

logger = get_logger(__name__)


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_service = UserService(db)

    async def login(self, data: UserLogin) -> Token:
        user = await self.user_service.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            logger.warning("Failed login attempt", extra={"email": data.email})
            raise UnauthorizedException("Invalid email or password.")
        if not user.is_active:
            raise UnauthorizedException("Account is deactivated.")

        token = self._generate_tokens(user)
        logger.info("User logged in", extra={"user_id": str(user.id)})
        return token

    async def refresh(self, refresh_token: str) -> Token:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid or expired refresh token.")

        user = await self.user_service.get_by_email(payload["sub"])
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive.")

        return self._generate_tokens(user)

    def _generate_tokens(self, user: User) -> Token:
        return Token(
            access_token=create_access_token(str(user.email), user.role),
            refresh_token=create_refresh_token(str(user.email)),
        )
