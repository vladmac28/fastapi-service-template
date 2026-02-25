from __future__ import annotations

import time
from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import async_session_maker
from app.core.errors import err
from app.core.redis import redis_client
from app.core.security import decode_access_token
from app.db.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


async def rate_limit(request: Request) -> None:
    ip = _client_ip(request)
    now = int(time.time())
    window = now // 60
    key = f"rl:{ip}:{window}"

    count = await redis_client.incr(key)
    if count == 1:
        await redis_client.expire(key, 120)

    from app.core.config import settings

    if count > settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=429,
            detail=err("rate_limited", "Too many requests, try later."),
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail=err("auth_required", "Missing bearer token."))

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail=err("invalid_token", "Invalid or expired token."))

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail=err("invalid_token", "Token has no subject."))

    q = await db.execute(select(User).where(User.email == sub))
    user = q.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail=err("user_not_found", "User not found."))
    if not user.is_active:
        raise HTTPException(status_code=403, detail=err("inactive_user", "User is inactive."))

    return user


def require_superuser(user: User = Depends(get_current_user)) -> User:
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail=err("forbidden", "Superuser required."))
    return user
