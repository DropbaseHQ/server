from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from server.settings import config

DB_USER = config.get("postgres_db_user")
DB_PASS = config.get("postgres_db_pass")
DB_HOST = config.get("postgres_db_host")
DB_PORT = config.get("postgres_db_port") or 5432
DB_NAME = config.get("postgres_db_name")

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
