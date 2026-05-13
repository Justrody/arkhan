from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user

from app.models import User, Paper, Vote
from app.schemas.vote import VoteStatus

from app.services.stats import update_user_stats

router = APIRouter(prefix="/papers/{paper_slug}/vote", tags=["Votes"])


def get_paper_by_slug(slug: str, db: Session) -> Paper:
    paper = db.query(Paper).filter(Paper.slug == slug).first()

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="paper not found",
        )

    if not paper.is_published:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="paper not found",
        )

    return paper


@router.get("/", response_model=VoteStatus)
def get_vote_status(
    paper_slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    paper = get_paper_by_slug(paper_slug, db)

    vote = db.query(Vote).filter(
        Vote.paper_id == paper.id,
        Vote.user_id == current_user.id,
    ).first()

    return VoteStatus(
        paper_id=paper.id,
        has_voted=vote is not None,
        vote_count=paper.vote_count,
    )


@router.post(
    "/",
    response_model=VoteStatus,
    status_code=status.HTTP_201_CREATED
)
def upvote_paper(
    paper_slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    paper = get_paper_by_slug(paper_slug, db)

    existing_vote = db.query(Vote).filter(
        Vote.paper_id == paper.id,
        Vote.user_id == current_user.id,
    ).first()

    if existing_vote:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="you have already voted on this paper",
        )

    new_vote = Vote(
        paper_id=paper.id,
        user_id=current_user.id,
    )

    db.add(new_vote)
    paper.vote_count += 1

    db.commit()

    update_user_stats(db, paper.author_id)

    return VoteStatus(
        paper_id=paper.id,
        has_voted=True,
        vote_count=paper.vote_count,
    )


@router.delete("/", response_model=VoteStatus)
def remove_vote(
    paper_slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    paper = get_paper_by_slug(paper_slug, db)

    vote = db.query(Vote).filter(
        Vote.paper_id == paper.id,
        Vote.user_id == current_user.id,
    ).first()

    if not vote:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="you have not voted on this paper",
        )

    db.delete(vote)

    paper.vote_count -= 1
    if paper.vote_count < 0:
        paper.vote_count = 0

    db.commit()

    update_user_stats(db, paper.author_id)

    return VoteStatus(
        paper_id=paper.id,
        has_voted=False,
        vote_count=paper.vote_count,
    )
