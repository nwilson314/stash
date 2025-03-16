from fastapi import Depends, HTTPException
from sqlmodel import Session, select

from stash.core.lib import FastApiRouter
from stash.core.security import get_current_user
from stash.db import get_session
from stash.models.categories import Category
from stash.models.users import User
from stash.schemas.category import CategoryCreate
from stash.schemas.response_models import DELETE_OK, RESPONSE_404

router = FastApiRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.get("/")
async def get_categories(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[Category]:
    """Get all categories for the current user."""
    categories = db.exec(
        select(Category)
        .where(Category.user_id == current_user.id)
        .order_by(Category.name)
    ).all()
    return categories


@router.post("/")
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Category:
    """Create a new category."""
    # Check if category with same name already exists
    existing = db.exec(
        select(Category).where(
            Category.user_id == current_user.id,
            Category.name == category.name
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    
    # Create new category
    new_category = Category(
        name=category.name.strip(),
        user_id=current_user.id,
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


@router.patch("/{category_id}")
async def update_category(
    category_id: int,
    category_data: CategoryCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Category:
    """Update a category."""
    # Get the category
    category = db.exec(
        select(Category).where(
            Category.id == category_id,
            Category.user_id == current_user.id
        )
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if new name conflicts with existing category
    if category_data.name != category.name:
        existing = db.exec(
            select(Category).where(
                Category.user_id == current_user.id,
                Category.name == category_data.name,
                Category.id != category_id
            )
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Category with this name already exists")
    
    # Update category
    category.name = category_data.name.strip()
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Delete a category."""
    # Get the category
    category = db.exec(
        select(Category).where(
            Category.id == category_id,
            Category.user_id == current_user.id
        )
    ).first()
    
    if not category:
        return RESPONSE_404
    
    # Delete the category
    db.delete(category)
    db.commit()
    return DELETE_OK
