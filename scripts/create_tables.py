from financial_intelligence_platform.db.postgres.base import Base
from financial_intelligence_platform.db.postgres.database import engine

import financial_intelligence_platform.db.postgres.models

Base.metadata.create_all(bind=engine)

print("Tables created successfully")
