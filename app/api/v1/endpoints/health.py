from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.schemas.response import APIResponse

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Health check", response_model=APIResponse[dict])
async def health_check():
    return APIResponse.ok(
        {"app": settings.APP_NAME, "version": settings.APP_VERSION, "status": "healthy"}
    )


@router.get("/health/db", summary="Database health check", response_model=APIResponse[dict])
async def db_health_check(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return APIResponse.ok({"database": "connected"})
