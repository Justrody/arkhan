import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)

    password = Column(String(255), nullable=False)

    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    reputation_points = Column(Integer, default=0, nullable=False)
    papers_count = Column(Integer, default=0, nullable=False)
    votes_received = Column(Integer, default=0, nullable=False)

    last_login = Column(DateTime, nullable=True)
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

    papers = relationship(
        "Paper", back_populates="author", cascade="all, delete-orphan"
    )
    votes = relationship(
        "Vote", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
