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
from stash.schemas.response_models import DELETE_OK, RESPONSE_404
from stash.schemas.security import AuthResponse, Token
from stash.schemas.users import UserCreate, UserResponse, UserUpdate
from stash.schemas.newsletter import NewsletterPreferences


router = FastApiRouter(
    prefix="/users",
    tags=["users"],
)


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


@router.delete("/delete", responses=RESPONSE_404)
def delete_user(user: UserCreate, db: Session = Depends(get_session)) -> None:
    db_user = db.exec(select(User).where(User.email == user.email)).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    # if not verify_password(user.password, db_user.hashed_password):
    #     raise HTTPException(status_code=401, detail="Invalid credentials")
    db.delete(db_user)
    db.commit()
    return DELETE_OK


@router.patch("/newsletter-preferences")
def update_newsletter_preferences(
    preferences: NewsletterPreferences,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Update a user's newsletter preferences"""
    # Validate frequency
    valid_frequencies = ["weekly", "biweekly", "monthly"]
    if preferences.frequency not in valid_frequencies:
        raise HTTPException(
            status_code=400,
            detail=f"Frequency must be one of: {', '.join(valid_frequencies)}",
        )

    # Update user preferences
    current_user.newsletter_enabled = preferences.enabled
    current_user.newsletter_frequency = preferences.frequency
    db.commit()

    return {
        "status": "success",
        "message": "Newsletter preferences updated",
        "preferences": {
            "enabled": current_user.newsletter_enabled,
            "frequency": current_user.newsletter_frequency,
        },
    }


@router.get("/newsletter-preferences")
def get_newsletter_preferences(
    db: Session = Depends(get_session), current_user: User = Depends(get_current_user)
) -> dict:
    """Get a user's newsletter preferences"""
    return {
        "enabled": current_user.newsletter_enabled,
        "frequency": current_user.newsletter_frequency,
    }

@router.get("/")
def get_all_users(
    db: Session = Depends(get_session),
) -> list[User]:
    return db.exec(select(User)).all()


@router.patch("/{user_id}")
def patch_user(
    user_update: UserUpdate,
    user_id: int,
    db: Session = Depends(get_session)
) -> User:
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
        