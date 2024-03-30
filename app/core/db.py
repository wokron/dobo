from sqlmodel import SQLModel, create_engine

from app.core.config import settings
from app import models  # don't remove this

engine = create_engine(str(settings.DATABASE_URI))

SQLModel.metadata.create_all(engine)
