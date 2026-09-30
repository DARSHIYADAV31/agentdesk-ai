import jwt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.user_model import User
from app.schemas.auth import LoginRequest, RefreshRequest, TokenPair
from app.security.deps import unauthorized
from app.security.jwt import create_access_token, create_refresh_token, decode_token
from app.security.passwords import verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


def issue_tokens(username: str) -> TokenPair:
    return TokenPair(access_token=create_access_token(username),
                     refresh_token=create_refresh_token(username))


@router.post("/login", response_model=TokenPair)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == body.username))
    # Same error for unknown user and bad password: don't reveal which usernames exist.
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Incorrect username or password")
    return issue_tokens(user.username)


@router.post("/refresh", response_model=TokenPair)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    try:
        username = decode_token(body.refresh_token, "refresh")
    except jwt.PyJWTError:
        raise unauthorized()
    if db.scalar(select(User).where(User.username == username)) is None:
        raise unauthorized()
    return issue_tokens(username)
