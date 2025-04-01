from typing import Generator

from sqlmodel import SQLModel, Session, create_engine
from stash.config import settings
from loguru import logger

# Create database engine
engine = create_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    logger.info("Initializing database...")
    SQLModel.metadata.create_all(engine)
    logger.info("Database initialization complete")


if __name__ == "__main__":
    create_db_and_tables()
