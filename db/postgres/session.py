from sqlalchemy.orm import sessionmaker

from db.postgres.database import engine

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
