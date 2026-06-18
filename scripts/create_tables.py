from db.postgres.base import Base
from db.postgres.database import engine

import db.postgres.models

Base.metadata.create_all(bind=engine)

print("Tables created successfully")
