from fastapi import APIRouter
from sqlalchemy import text

from app.core.db import async_session_maker

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    async with async_session_maker() as session:
        await session.execute(text("SELECT 1"))
    return {"status": "ok"}
