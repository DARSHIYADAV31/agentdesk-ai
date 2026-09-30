import getpass
import sys

from app.db import models  # noqa: F401
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.db.user_model import User
from app.security.passwords import hash_password


def main() -> None:
    """Usage: python -m app.db.create_user <username> <agent|admin>"""
    username, role = sys.argv[1], sys.argv[2]
    Base.metadata.create_all(engine)
    password = getpass.getpass("Password: ")
    with SessionLocal() as db:
        db.add(User(username=username, password_hash=hash_password(password), role=role))
        db.commit()
    print(f"Created {role} user {username}")


if __name__ == "__main__":
    main()
