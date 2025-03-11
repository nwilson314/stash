from fastapi import HTTPException, Depends
from sqlmodel import Session, select, col

from stash.core.lib import FastApiRouter
from stash.core.security import get_current_user
from stash.db import get_session
from stash.models.links import Link
from stash.models.users import User
from stash.services import get_link_service
from stash.services.links import LinkService
from stash.schemas.response_models import DELETE_OK, RESPONSE_404

router = FastApiRouter(
    prefix="/links",
    tags=["links"],
)


@router.get("/")
def get_links(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)) -> list[Link]:
    links = db.exec(select(Link).where(Link.user_id == current_user.id).order_by(col(Link.updated_at).desc())).all()
    return links


@router.patch("/{link_id}/read")
def mark_link_read(link_id: int, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    link = db.exec(select(Link).where(Link.id == link_id, Link.user_id == current_user.id)).first()
    if not link:
        raise HTTPException(status_code=404, detail="link not found")
    link.read = not link.read
    db.commit()
    db.refresh(link)
    return link


@router.delete("/{link_id}", response_model=dict[str, bool], responses=RESPONSE_404)
def delete_link(link_id: int, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)) -> None:
    db_link = db.exec(select(Link).where(Link.id == link_id, Link.user_id == current_user.id)).first()
    if not db_link:
        raise HTTPException(status_code=404, detail="link not found")
    db.delete(db_link)
    db.commit()
    return DELETE_OK


@router.post("/save")
async def save_link(
    link_data: Link,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    link_service: LinkService = Depends(get_link_service),
) -> Link:
    # Process the URL
    metadata = await link_service.process_new_link(link_data.url)
    if metadata.error:
        raise HTTPException(status_code=400, detail=metadata.error)

    # Create link with processed metadata
    link = Link(
        url=str(metadata.final_url or metadata.url),  # Use final URL if available
        original_url=str(metadata.url),
        title=metadata.title or str(metadata.url),  # Fallback to URL if no title
        content_type=metadata.content_type,
        user_id=current_user.id,
        note=link_data.note,
    )
    
    db.add(link)
    db.commit()
    db.refresh(link)
    
    return link


@router.post("/migrate-orphaned-links", response_model=dict[str, int])
def migrate_orphaned_links(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)) -> dict[str, int]:
    """Temporary endpoint to migrate links without a user_id to the current user."""
    orphaned_links = db.exec(select(Link).where(Link.user_id == None)).all()
    count = len(orphaned_links)
    
    for link in orphaned_links:
        link.user_id = current_user.id
    
    db.commit()
    return {"migrated_count": count}
