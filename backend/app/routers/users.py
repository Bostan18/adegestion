"""Profil courant et gestion des utilisateurs de l'agence.

La creation d'un compte se fait dans Supabase Auth. Cette API gere le profil
applicatif associe, dont le role, et reste reservee a l'admin.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import AdminUser, CurrentUser
from app.models.user import User
from app.schemas.common import Page
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(tags=["utilisateurs"])

DbSession = Annotated[Session, Depends(get_db)]


@router.get("/me", response_model=UserRead, summary="Profil de l'utilisateur connecte")
def read_me(current_user: CurrentUser) -> User:
    return current_user


@router.get("/users", response_model=Page[UserRead], summary="Lister les utilisateurs")
def list_users(
    db: DbSession,
    _: AdminUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[UserRead]:
    total = db.scalar(select(func.count()).select_from(User)) or 0
    rows = db.scalars(
        select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
    ).all()
    return Page[UserRead](
        items=[UserRead.model_validate(row) for row in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/users",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Creer le profil d'un compte Supabase Auth",
)
def create_user(payload: UserCreate, db: DbSession, _: AdminUser) -> User:
    if db.get(User, payload.id) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un profil existe deja pour cet identifiant.",
        )
    existing_email = db.scalar(select(User).where(User.email == payload.email))
    if existing_email is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cette adresse email est deja utilisee.",
        )

    user = User(
        id=payload.id,
        email=str(payload.email),
        full_name=payload.full_name,
        role=str(payload.role),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}", response_model=UserRead, summary="Modifier un utilisateur")
def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    db: DbSession,
    current_user: AdminUser,
) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable."
        )

    data = payload.model_dump(exclude_unset=True)
    if (
        "role" in data
        and user.id == current_user.id
        and str(data["role"]) != current_user.role
    ):
        # Evite qu'un admin se retire lui-meme ses droits par erreur.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas modifier votre propre role.",
        )

    for field, value in data.items():
        setattr(user, field, str(value) if field == "role" else value)

    db.commit()
    db.refresh(user)
    return user
