"""Dependances d'authentification et de controle des roles."""

import uuid
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import (
    AuthNotConfiguredError,
    InvalidTokenError,
    decode_token,
)
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False, description="Jeton d'acces Supabase")

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Jeton d'authentification invalide ou expire.",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Valide le jeton Supabase et retourne le profil correspondant."""
    if credentials is None or not credentials.credentials:
        raise CREDENTIALS_EXCEPTION

    try:
        identity = decode_token(credentials.credentials)
    except AuthNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentification non configuree sur le serveur.",
        ) from exc
    except InvalidTokenError as exc:
        raise CREDENTIALS_EXCEPTION from exc

    try:
        user_id = uuid.UUID(identity.user_id)
    except ValueError as exc:
        raise CREDENTIALS_EXCEPTION from exc

    user = db.get(User, user_id)
    if user is None:
        # Le compte existe dans Supabase Auth mais n'a pas de profil dans
        # l'agence : on refuse plutot que de deviner un role.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Aucun profil utilisateur n'est associe a ce compte.",
        )

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: UserRole) -> Callable[[User], User]:
    """Construit une dependance qui n'accepte que les roles donnes."""
    allowed = {str(role) for role in roles}

    def dependency(current_user: CurrentUser) -> User:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Votre role ne permet pas cette action.",
            )
        return current_user

    return dependency


# Raccourcis correspondant au RBAC decrit dans docs/ARCHITECTURE.md.
require_admin = require_roles(UserRole.ADMIN)
require_property_manager = require_roles(UserRole.ADMIN, UserRole.AGENT)
require_accountant = require_roles(UserRole.ADMIN, UserRole.COMPTABLE)

AdminUser = Annotated[User, Depends(require_admin)]
PropertyManagerUser = Annotated[User, Depends(require_property_manager)]
AccountantUser = Annotated[User, Depends(require_accountant)]
