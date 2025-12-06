from datetime import datetime

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.config import settings

from app.schemas.user import UserResponse


class PaperBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=settings.max_paper_title)
    content: str = Field(
        ..., min_length=50, max_length=settings.max_paper_content
    )
    tags: Optional[list[str]] = Field(default_factory=list)


class PaperCreate(PaperBase):
    is_published: bool = True


class PaperUpdate(BaseModel):
    title: Optional[str] = Field(
        None, min_length=5, max_length=settings.max_paper_title
    )
    content: Optional[str] = Field(
        None, min_length=50, max_length=settings.max_paper_content
    )
    tags: Optional[list[str]] = None
    is_published: Optional[bool] = None


class PaperResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    title: str
    slug: str

    tags: list[str] = []

    author: UserResponse

    vote_count: int = 0
    is_published: bool = True

    created_at: datetime
    published_at: Optional[datetime] = None


class PaperDetail(PaperResponse):
    content: str
    content_html: str = ""
    user_has_voted: bool = False


class PaperList(BaseModel):
    papers: list[PaperResponse]

    total: int
    page: int
    page_size: int
    total_pages: int


class MarkdownPreview(BaseModel):
    content: str = Field(..., max_length=settings.max_paper_content)


class MarkdownPreviewResponse(BaseModel):
    html: str
