from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, rate_limit
from app.core.errors import err
from app.core.security import create_access_token
from app.db.models.user import User
from app.schemas.auth import LoginIn, RegisterIn, TokenOut
from app.schemas.user import UserOut
from app.services.users import authenticate_user, create_user, get_user_by_email

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=UserOut, dependencies=[Depends(rate_limit)])
async def register(payload: RegisterIn, db: AsyncSession = Depends(get_db)) -> UserOut:
    existing = await get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=409, detail=err("email_taken", "Email already registered."))

    user = await create_user(db, payload.email, payload.password)
    return UserOut(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("/login", response_model=TokenOut, dependencies=[Depends(rate_limit)])
async def login(payload: LoginIn, db: AsyncSession = Depends(get_db)) -> TokenOut:
    user = await authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail=err("bad_credentials", "Invalid email or password."))

    token = create_access_token(subject=user.email)
    return TokenOut(access_token=token)


@router.get("/me", response_model=UserOut)
async def me(current: User = Depends(get_current_user)) -> UserOut:
    return UserOut(
        id=current.id,
        email=current.email,
        is_active=current.is_active,
        is_superuser=current.is_superuser,
        created_at=current.created_at,
        updated_at=current.updated_at,
    )
