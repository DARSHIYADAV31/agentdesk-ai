from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.db.user_model import User
from app.security.deps import current_user

router = APIRouter(prefix="/auth", tags=["auth"])


class Profile(BaseModel):
    username: str
    role: str


@router.get("/me", response_model=Profile)
def me(user: User = Depends(current_user)):
    return Profile(username=user.username, role=user.role)
