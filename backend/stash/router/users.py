from collections import defaultdict
from fastapi import HTTPException, Depends
from sqlmodel import Session, select

from stash.core.lib import FastApiRouter
from stash.config import settings
from stash.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    get_current_user,
)
from stash.db import get_session
from stash.models.users import User
from stash.models.links import Link
from stash.schemas.links import LinkActivity
from stash.schemas.response_models import DELETE_OK, RESPONSE_404, UPDATE_OK
from stash.schemas.security import AuthResponse, Token
from stash.schemas.users import UserCreate, UserResponse, UserUpdate, UserPassword


router = FastApiRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    db_user = db.exec(select(User).where(User.id == user_id)).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    print(db_user)
    return db_user


@router.patch("/{user_id}")
def patch_user(
    user_update: UserUpdate,
    user_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    db_user = db.exec(select(User).where(User.id == user_id)).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    update_date = user_update.model_dump(exclude_none=True)
    for key, value in update_date.items():
        setattr(db_user, key, value)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/{user_id}/activity")
def get_user_activity(
    user_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> LinkActivity:
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    db_links = db.exec(select(Link).where(Link.user_id == user_id)).all()
    link_data = defaultdict(int)
    for link in db_links:
        link_data[link.created_at.strftime("%Y-%m-%d")] += 1
    return LinkActivity(days=link_data)


@router.post("/register", response_model=AuthResponse)
def register_user(user: UserCreate, db: Session = Depends(get_session)) -> AuthResponse:
    if db.exec(select(User).where(User.email == user.email)).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(
        email=user.email,
        username=user.username,
        hashed_password=get_password_hash(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=settings.JWT_EXPIRE_MINUTES
    )

    return AuthResponse(
        token=Token(
            access_token=access_token,
            token_type="bearer",
        ),
        user=UserResponse(
            id=new_user.id,
            email=new_user.email,
            username=new_user.username,
        ),
    )


@router.post("/login", response_model=AuthResponse)
def login_user(user: UserCreate, db: Session = Depends(get_session)) -> AuthResponse:
    db_user = db.exec(select(User).where(User.email == user.email)).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Invalid credentials")
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=settings.JWT_EXPIRE_MINUTES
    )

    return AuthResponse(
        token=Token(
            access_token=access_token,
            token_type="bearer",
        ),
        user=UserResponse(
            id=db_user.id,
            email=db_user.email,
            username=db_user.username,
        ),
    )


@router.delete("/{user_id}", responses=RESPONSE_404)
def delete_user(user_id: int, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)) -> None:
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    db_user = db.exec(select(User).where(User.id == user_id)).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return DELETE_OK


@router.patch("/update-password", responses=RESPONSE_404)
def update_password(
    user_pass: UserPassword,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> None:
    db_user = db.exec(select(User).where(User.id == user.id)).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user_pass.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    db_user.hashed_password = get_password_hash(user_pass.new_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UPDATE_OK
    
    