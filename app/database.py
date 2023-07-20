from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from .config import settings

dbname = settings.DATABASE_NAME
user = settings.DATABASE_USERNAME
password = settings.DATABASE_PASSWORD
host = settings.DATABASE_HOSTNAME
port = settings.DATABASE_PORT

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg://{user}:{password}@{host}:{port}/{dbname}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
Session = Session


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
