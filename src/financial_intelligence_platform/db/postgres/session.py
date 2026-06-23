from sqlalchemy.orm import sessionmaker

from financial_intelligence_platform.db.postgres.database import engine

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
