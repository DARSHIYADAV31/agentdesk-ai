from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.auth import issue_tokens
from app.db.session import get_db
from app.db.user_model import User
from app.schemas.auth import TokenPair
from app.schemas.register import RegisterRequest
from app.security.passwords import hash_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenPair, status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    # Role is fixed to "agent": admins (who approve actions) are created only via the CLI.
    db.add(User(username=body.username, password_hash=hash_password(body.password), role="agent"))
    try:
        db.commit()
    except IntegrityError:  # the unique index also covers two simultaneous sign-ups
        db.rollback()
        raise HTTPException(409, "Username is already taken")
    return issue_tokens(body.username)
