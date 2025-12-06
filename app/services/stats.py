from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import User, Paper


def update_user_stats(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    papers_count = db.query(func.count(Paper.id)).filter(
        Paper.author_id == user_id,
        Paper.is_published
    ).scalar() or 0

    user.papers_count = papers_count

    db.commit()
    db.refresh(user)

    return user


def recalculate_all_user_stats(db: Session):
    users = db.query(User).all()
    for user in users:
        update_user_stats(db, user.id)
