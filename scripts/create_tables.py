import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db.postgres.base import Base
from db.postgres.database import engine

import db.postgres.models

Base.metadata.create_all(bind=engine)

print("Tables created successfully")
