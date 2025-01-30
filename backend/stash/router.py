from fastapi import APIRouter, Depends
from sqlmodel import Session, select, col

from stash.schemas import LinkCreate
from stash.db import get_session
from stash.models import Link

router = APIRouter()


@router.get("/links")
def get_links(db: Session = Depends(get_session)) -> list[Link]:
    links = db.exec(select(Link).order_by(col(Link.timestamp).desc())).all()
    return links


@router.post("/save")
def save_link(link: LinkCreate, db: Session = Depends(get_session)) -> Link:
    db_link = Link(url=link.url, note=link.note)
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link
