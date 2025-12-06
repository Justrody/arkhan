from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, DateTime, Text, ForeignKey, Boolean
)
from sqlalchemy.orm import relationship

from app.database import Base


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)

    content = Column(Text, nullable=False)

    tags = Column(String(255), nullable=True)

    is_published = Column(Boolean, default=True, nullable=False)
    vote_count = Column(Integer, default=0, nullable=False)

    published_at = Column(DateTime, nullable=True)
    created_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        nullable=False
    )

    author = relationship("User", back_populates="papers")
    votes = relationship(
        "Vote", back_populates="paper", cascade="all, delete-orphan"
    )

    @property
    def tags_list(self) -> list[str]:
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]

    @tags_list.setter
    def tags_list(self, value: list[str]):
        self.tags = ",".join(tag.strip() for tag in value if tag.strip())
