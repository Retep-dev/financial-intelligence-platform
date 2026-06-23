from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from financial_intelligence_platform.core.config.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
