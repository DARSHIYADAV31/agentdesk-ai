from datetime import datetime, timedelta, timezone

import jwt

from app.config import get_settings


def _encode(subject: str, kind: str, lifetime: timedelta) -> str:
    settings = get_settings()
    if not settings.jwt_secret:
        raise RuntimeError("JWT_SECRET is not set")
    now = datetime.now(timezone.utc)
    claims = {"sub": subject, "type": kind, "iat": now, "exp": now + lifetime}
    return jwt.encode(claims, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str) -> str:
    return _encode(subject, "access", timedelta(minutes=get_settings().access_token_minutes))


def create_refresh_token(subject: str) -> str:
    return _encode(subject, "refresh", timedelta(days=get_settings().refresh_token_days))


def decode_token(token: str, kind: str) -> str:
    """Return the subject; raises jwt.PyJWTError if invalid, expired or the wrong kind."""
    settings = get_settings()
    claims = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    if claims.get("type") != kind:
        raise jwt.InvalidTokenError("wrong token type")
    return claims["sub"]
