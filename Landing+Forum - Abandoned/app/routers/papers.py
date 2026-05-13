from datetime import datetime, timezone

import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query

from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from app.database import get_db

from app.services.stats import update_user_stats
from app.services.markdown import render_markdown

from app.models import User, Paper, Vote
from app.schemas.paper import (
    PaperCreate,
    PaperUpdate,
    PaperResponse,
    PaperDetail,
    PaperList,
    MarkdownPreview,
    MarkdownPreviewResponse,
)
from app.schemas.user import UserResponse

from app.dependencies import (
    get_current_user, get_current_user_optional, Pagination
)

router = APIRouter(prefix="/papers", tags=["Papers"])


def generate_slug(title: str, paper_id: Optional[int] = None) -> str:
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[-\s]+", "-", slug).strip("-")

    if paper_id:
        slug = f"{slug}-{paper_id}"

    return slug[:250]


def build_paper_response(
    paper: Paper, current_user: Optional[User] = None
) -> PaperResponse:
    return PaperResponse(
        id=paper.id,
        title=paper.title,
        slug=paper.slug,
        tags=paper.tags_list,
        author=UserResponse.model_validate(paper.author),
        vote_count=paper.vote_count,
        is_published=paper.is_published,
        created_at=paper.created_at,
        published_at=paper.published_at,
    )


def build_paper_detail(
    paper: Paper,
    current_user: Optional[User] = None,
    db: Optional[Session] = None,
) -> PaperDetail:
    user_has_voted = False

    if current_user and db:
        vote = db.query(Vote).filter(
            Vote.paper_id == paper.id,
            Vote.user_id == current_user.id,
        ).first()
        user_has_voted = vote is not None

    return PaperDetail(
        id=paper.id,
        title=paper.title,
        slug=paper.slug,
        tags=paper.tags_list,
        author=UserResponse.model_validate(paper.author),
        vote_count=paper.vote_count,
        is_published=paper.is_published,
        created_at=paper.created_at,
        published_at=paper.published_at,
        content=paper.content,
        content_html=render_markdown(paper.content),
        user_has_voted=user_has_voted,
    )


@router.get("/", response_model=PaperList)
def list_papers(
    sort: str = Query("recent", enum=["recent", "trending", "top"]),
    tag: Optional[str] = None,
    search: Optional[str] = None,
    pagination: Pagination = Depends(),
    db: Session = Depends(get_db),
):
    query = db.query(Paper).options(
        joinedload(Paper.author)
    ).filter(Paper.is_published)

    if tag:
        query = query.filter(Paper.tags.contains(tag))

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Paper.title.ilike(search_term)) |
            (Paper.tags.ilike(search_term))
        )

    total = query.count()

    if sort == "recent":
        query = query.order_by(
            desc(Paper.published_at), desc(Paper.created_at)
        )
    elif sort == "trending":
        query = query.order_by(
            desc(Paper.vote_count),
            desc(Paper.published_at),
        )
    elif sort == "top":
        query = query.order_by(
            desc(Paper.vote_count), desc(Paper.published_at)
        )

    papers = query.offset(pagination.offset).limit(pagination.page_size).all()

    total_pages = (total + pagination.page_size - 1) // pagination.page_size

    return PaperList(
        papers=[build_paper_response(p) for p in papers],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
    )


@router.get("/my", response_model=PaperList)
def list_my_papers(
    include_drafts: bool = False,
    pagination: Pagination = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Paper).options(
        joinedload(Paper.author)
    ).filter(Paper.author_id == current_user.id)

    if not include_drafts:
        query = query.filter(Paper.is_published)

    total = query.count()

    papers = query.order_by(desc(Paper.created_at)).offset(
        pagination.offset
    ).limit(pagination.page_size).all()

    total_pages = (total + pagination.page_size - 1) // pagination.page_size

    return PaperList(
        papers=[build_paper_response(p) for p in papers],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
    )


@router.get("/user/{username}", response_model=PaperList)
def list_user_papers(
    username: str,
    pagination: Pagination = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found",
        )

    query = db.query(Paper).options(
        joinedload(Paper.author)
    ).filter(
        Paper.author_id == user.id,
        Paper.is_published,
    )

    total = query.count()

    papers = query.order_by(desc(Paper.published_at)).offset(
        pagination.offset
    ).limit(pagination.page_size).all()

    total_pages = (total + pagination.page_size - 1) // pagination.page_size

    return PaperList(
        papers=[build_paper_response(p) for p in papers],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
    )


@router.post(
    "/",
    response_model=PaperDetail,
    status_code=status.HTTP_201_CREATED
)
def create_paper(
    paper_data: PaperCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_paper = Paper(
        title=paper_data.title,
        slug="temp",
        content=paper_data.content,
        author_id=current_user.id,
        is_published=paper_data.is_published,
    )

    if paper_data.tags:
        new_paper.tags_list = paper_data.tags

    if paper_data.is_published:
        new_paper.published_at = datetime.now(timezone.utc)

    db.add(new_paper)
    db.flush()

    new_paper.slug = generate_slug(new_paper.title, new_paper.id)

    db.commit()
    db.refresh(new_paper)

    update_user_stats(db, current_user.id)

    return build_paper_detail(new_paper, current_user, db)


@router.get("/{slug}", response_model=PaperDetail)
def get_paper(
    slug: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    paper = db.query(Paper).options(
        joinedload(Paper.author)
    ).filter(Paper.slug == slug).first()

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="paper not found",
        )

    if not paper.is_published:
        if not current_user or current_user.id != paper.author_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="paper not found",
            )

    return build_paper_detail(paper, current_user, db)


@router.put("/{slug}", response_model=PaperDetail)
def update_paper(
    slug: str,
    paper_data: PaperUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    paper = db.query(Paper).filter(Paper.slug == slug).first()

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="paper not found",
        )

    if paper.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized to update this paper",
        )

    update_dict = paper_data.model_dump(exclude_unset=True)

    for field, value in update_dict.items():
        if field == "tags":
            paper.tags_list = value
        else:
            setattr(paper, field, value)

    if "title" in update_dict:
        paper.slug = generate_slug(paper.title, paper.id)

    if paper_data.is_published and not paper.published_at:
        paper.published_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(paper)

    return build_paper_detail(paper, current_user, db)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
def delete_paper(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    paper = db.query(Paper).filter(Paper.slug == slug).first()

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="paper not found",
        )

    if paper.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized to delete this paper",
        )

    db.delete(paper)
    db.commit()


@router.post("/preview", response_model=MarkdownPreviewResponse)
def preview_markdown(
    preview_data: MarkdownPreview,
):
    html = render_markdown(preview_data.content)
    return MarkdownPreviewResponse(html=html)
