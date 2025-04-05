from fastapi import BackgroundTasks, HTTPException, Depends
from sqlmodel import Session, select, col
from loguru import logger

from stash.core.lib import FastApiRouter
from stash.core.security import get_current_user
from stash.db import get_session
from stash.models.categories import Category
from stash.models.links import Link, ProcessingStatus
from stash.models.users import User
from stash.services import get_link_service, get_ai_service
from stash.services.ai import AIService
from stash.services.links import LinkService
from stash.schemas.response_models import DELETE_OK, RESPONSE_404

router = FastApiRouter(
    prefix="/links",
    tags=["links"],
)


@router.get("/")
async def get_links(
    db: Session = Depends(get_session), current_user: User = Depends(get_current_user)
) -> list[Link]:
    links = db.exec(
        select(Link)
        .where(Link.user_id == current_user.id)
        .order_by(col(Link.updated_at).desc())
    ).all()
    return links


@router.get("/{link_id}")
async def get_link(
    link_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Link:
    link = db.exec(
        select(Link).where(Link.id == link_id, Link.user_id == current_user.id)
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="link not found")
    return link


@router.patch("/{link_id}/read")
async def mark_link_read(
    link_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    link = db.exec(
        select(Link).where(Link.id == link_id, Link.user_id == current_user.id)
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="link not found")
    link.read = not link.read
    db.commit()
    db.refresh(link)
    return link


@router.patch("/{link_id}/category")
async def update_link_category(
    link_id: int,
    category_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Link:
    link = db.exec(
        select(Link).where(Link.id == link_id, Link.user_id == current_user.id)
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="link not found")
    if category_id < 0:
        link.category_id = None
        db.commit()
        db.refresh(link)
        return link
    if not db.exec(select(Category).where(Category.id == category_id)).first():
        raise HTTPException(status_code=404, detail="category not found")
    link.category_id = category_id
    db.commit()
    db.refresh(link)
    return link


@router.delete("/{link_id}", response_model=dict[str, bool], responses=RESPONSE_404)
async def delete_link(
    link_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> None:
    db_link = db.exec(
        select(Link).where(Link.id == link_id, Link.user_id == current_user.id)
    ).first()
    if not db_link:
        raise HTTPException(status_code=404, detail="link not found")
    db.delete(db_link)
    db.commit()
    return DELETE_OK


@router.post("/save")
async def save_link(
    link_data: Link,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    link_service: LinkService = Depends(get_link_service),
    ai_service: AIService = Depends(get_ai_service),
) -> Link:
    # Process the URL
    metadata = await link_service.process_new_link(link_data.url)
    if metadata.error:
        print(metadata.error)
        raise HTTPException(status_code=400, detail=metadata.error)

    # Create link with processed metadata
    link = Link(
        url=str(metadata.final_url or metadata.url),  # Use final URL if available
        original_url=str(metadata.url),
        title=metadata.title or str(metadata.url),  # Fallback to URL if no title
        content_type=metadata.content_type,
        user_id=current_user.id,
        note=link_data.note,
        thumbnail_url=metadata.thumbnail_url,
        author=metadata.author,
        duration=metadata.duration,
        processing_status=ProcessingStatus.COMPLETE,
    )

    db.add(link)
    db.commit()
    db.refresh(link)

    # Pass the already processed metadata to the AI service
    background_tasks.add_task(
        ai_service.process_link, link.id, current_user.id, metadata
    )

    return link

@router.patch("/{link_id}/summarize")
async def summarize_link(
    link_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service),
    link_service: LinkService = Depends(get_link_service),
) -> Link:
    logger.info(f"Starting summarization for link {link_id} by user {current_user.id}")
    db_link = db.exec(
        select(Link).where(Link.id == link_id, Link.user_id == current_user.id)
    ).first()
    if not db_link:
        logger.warning(f"Link {link_id} not found for user {current_user.id}")
        raise HTTPException(status_code=404, detail="link not found")
    
    try:
        # Get summary from AI service
        logger.info(f"Calling AI service to summarize link {link_id}")
        summary = await ai_service.summarize_link(db_link, link_service)
        logger.info(f"Received summary for link {link_id}, length: {len(summary) if summary else 0}")
        
        # Update link with summary
        db_link.summary = summary
        
        # Commit changes to database
        try:
            db.commit()
            db.refresh(db_link)
            logger.info(f"Successfully updated link {link_id} with summary")
        except Exception as db_error:
            logger.error(f"Database error updating link {link_id}: {str(db_error)}")
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
        
        # Return the updated link
        return db_link
    except Exception as e:
        logger.error(f"Error summarizing link {link_id}: {str(e)}", exc_info=True)
        db.rollback()  # Make sure to rollback any pending changes
        raise HTTPException(status_code=500, detail=f"Failed to summarize link: {str(e)}")


@router.post("/migrate-orphaned-links", response_model=dict[str, int])
def migrate_orphaned_links(
    db: Session = Depends(get_session), current_user: User = Depends(get_current_user)
) -> dict[str, int]:
    """Temporary endpoint to migrate links without a user_id to the current user."""
    orphaned_links = db.exec(select(Link).where(Link.user_id == None)).all()
    count = len(orphaned_links)

    for link in orphaned_links:
        link.user_id = current_user.id

    db.commit()
    return {"migrated_count": count}
