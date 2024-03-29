from sqlmodel import create_engine

from app.core.config import Settings

engine = create_engine(str(Settings.SQLALCHEMY_DATABASE_URI))
