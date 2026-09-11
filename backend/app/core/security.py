"""Verification des jetons emis par Supabase Auth.

Supabase signe ses JWT en HS256 avec le secret du projet (Project Settings >
API > JWT Secret). On verifie la signature, l'expiration et l'audience, puis on
ne garde du jeton que l'identite. Le role applicatif, lui, est toujours relu en
base : la table `users` fait autorite, le claim du jeton ne sert qu'aux policies
RLS cote Supabase.
"""

from dataclasses import dataclass

import jwt

from app.core.config import settings


class InvalidTokenError(Exception):
    """Jeton absent, expire, mal signe ou incomplet."""


class AuthNotConfiguredError(Exception):
    """SUPABASE_JWT_SECRET n'est pas renseigne cote serveur."""


@dataclass(frozen=True)
class TokenIdentity:
    """Identite extraite d'un jeton Supabase valide."""

    user_id: str
    email: str | None
    # Role annonce par le jeton, conserve a titre indicatif seulement.
    claimed_role: str | None


def decode_token(token: str) -> TokenIdentity:
    if not settings.supabase_jwt_secret:
        raise AuthNotConfiguredError("SUPABASE_JWT_SECRET n'est pas configure.")

    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience=settings.supabase_jwt_audience,
            options={"require": ["exp", "sub"]},
        )
    except jwt.PyJWTError as exc:
        raise InvalidTokenError(str(exc)) from exc

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenError("Le jeton ne contient pas d'identifiant utilisateur.")

    app_metadata = payload.get("app_metadata") or {}
    claimed_role = app_metadata.get("role") or payload.get("user_role")

    return TokenIdentity(
        user_id=str(user_id),
        email=payload.get("email"),
        claimed_role=claimed_role,
    )
