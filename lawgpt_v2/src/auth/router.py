# src/auth/router.py

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from src.db.session import get_db
from src.auth import models, schemas, security
from src.auth.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: schemas.UserCreate, db: Annotated):
    """Создание нового пользователя."""
    hashed_password = security.get_password_hash(user_in.password)
    new_user = models.User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Имя пользователя или email уже существуют."
        )
    return new_user

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated,
    db: Annotated
):
    """Аутентификация пользователя и возврат JWT токена."""
    query = select(User).where(User.username == form_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.create_access_token(
        data={"sub": user.username, "user_id": user.id}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=schemas.UserOut)
async def read_users_me(current_user: Annotated):
    """Получение информации о текущем пользователе."""
    return current_user