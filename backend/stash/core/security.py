from datetime import datetime, timedelta

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from loguru import logger
from passlib.context import CryptContext
from sqlmodel import Session, select

from stash.config import settings
from stash.db import get_session
from stash.models.users import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: int | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    logger.info(f"Getting current user from token: {token}")

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        logger.info(f"Payload: {payload}")
        email: str | None = payload.get("sub")
        logger.info(f"Email: {email}")
        if email is None:
            logger.warning("Token payload missing 'sub' claim")
            raise credentials_exception
    except jwt.PyJWTError as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        raise credentials_exception

    user = db.exec(select(User).where(User.email == email)).first()
    if user is None:
        logger.warning(f"No user found for validated token")
        raise credentials_exception
    return user
