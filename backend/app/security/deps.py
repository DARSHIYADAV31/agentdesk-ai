import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.user_model import User
from app.security.jwt import decode_token

bearer = HTTPBearer(auto_error=False)


def unauthorized() -> HTTPException:
    return HTTPException(401, "Invalid or expired credentials",
                         headers={"WWW-Authenticate": "Bearer"})


def current_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer),
                 db: Session = Depends(get_db)) -> User:
    if creds is None:
        raise unauthorized()
    try:
        username = decode_token(creds.credentials, "access")
    except jwt.PyJWTError:
        raise unauthorized()
    user = db.scalar(select(User).where(User.username == username))
    if user is None:
        raise unauthorized()
    return user


def require_admin(user: User = Depends(current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(403, "Admin role required")
    return user
