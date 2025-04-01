from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Query
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

from sqlmodel import Session, select, func
from stash.db import get_session
from stash.models.users import User
from stash.services.newsletter import NewsletterService
from stash.services.email import EmailService
from stash.services.ai import AIService
from stash.config import settings


# Simple admin authentication - in production, use proper auth
def get_admin_user(api_key: str = Query(...)):
    if api_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


router = APIRouter(prefix="/admin", tags=["admin"])

logger = logging.getLogger(__name__)


@router.post("/newsletters/trigger")
async def trigger_newsletters(
    background_tasks: BackgroundTasks,
    batch_size: int = 50,
    days_back: int = 7,
    specific_user_id: Optional[int] = None,
    _: bool = Depends(get_admin_user),
    db: Session = Depends(get_session),
):
    """Trigger newsletter generation and sending

    This endpoint is meant to be called by an external cron service.
    It will process users in batches to avoid timeouts and excessive resource usage.
    """
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)

    # Initialize services
    email_service = EmailService()
    ai_service = AIService()
    newsletter_service = NewsletterService(email_service, ai_service)

    # If specific user is provided, just process that user
    if specific_user_id:
        background_tasks.add_task(
            newsletter_service.generate_and_send_newsletter,
            specific_user_id,
            start_date,
            end_date,
        )
        return {
            "status": "processing",
            "mode": "single_user",
            "user_id": specific_user_id,
        }

    # Get total user count with newsletter enabled
    user_count = db.exec(
        select(func.count()).select_from(User).where(User.newsletter_enabled == True)
    ).one()

    # Calculate number of batches
    num_batches = (user_count + batch_size - 1) // batch_size
    print(f"Total users: {user_count}, batches: {num_batches}")

    # Queue background tasks for each batch
    for batch in range(1, num_batches + 1):
        print(f"Queueing batch {batch} of {num_batches}")
        background_tasks.add_task(
            newsletter_service.process_batch, batch, batch_size, start_date, end_date
        )

    return {
        "status": "processing",
        "mode": "batch",
        "total_users": user_count,
        "batch_size": batch_size,
        "batches": num_batches,
    }
