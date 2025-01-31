from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, col

from stash.schemas import LinkCreate, DELETE_OK, RESPONSE_404
from stash.db import get_session
from stash.models import Link

router = APIRouter()


@router.get("/links")
def get_links(db: Session = Depends(get_session)) -> list[Link]:
    links = db.exec(select(Link).order_by(col(Link.timestamp).desc())).all()
    return links

@router.patch("/links/{link_id}/read")
def mark_link_read(link_id: int, db: Session = Depends(get_session)):
    link = db.exec(select(Link).where(Link.id == link_id)).first()
    if not link:
        raise HTTPException(status_code=404, detail="link not found")
    link.read = True
    db.commit()
    db.refresh(link)
    return link

@router.delete("/links/{link_id}", response_model=dict[str, bool], responses=RESPONSE_404)
def delete_link(link_id: int, db: Session = Depends(get_session)) -> None:
    db_link = db.exec(select(Link).where(Link.id == link_id)).first()
    db.delete(db_link)
    db.commit()
    return DELETE_OK

@router.post("/save")
def save_link(link: LinkCreate, db: Session = Depends(get_session)) -> Link:
    db_link = Link(url=link.url, note=link.note)
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link
