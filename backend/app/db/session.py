from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings

# pool_pre_ping drops dead connections instead of hanging on them.
engine = create_engine(get_settings().database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
