from typing import Generator

from sqlmodel import SQLModel, Session, create_engine
from stash.config import settings
from loguru import logger

# Create database engine
engine = create_engine(settings.DATABASE_URL, echo=False)

def get_session() -> Generator[Session, None, None]:
    logger.info(f"Getting session from url: {settings.DATABASE_URL}")
    with Session(engine) as session:
        yield session


if __name__ == "__main__":
    logger.info("Creating database")
    SQLModel.metadata.create_all(engine)
    logger.info("Database created")