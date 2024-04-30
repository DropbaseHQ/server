from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from server.settings import config

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://{0}:{1}@{2}:{3}/{4}".format(
    config["database"]["user"],
    config["database"]["pass"],
    config["database"]["host"],
    config["database"]["port"] or 5432,
    config["database"]["name"],
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
