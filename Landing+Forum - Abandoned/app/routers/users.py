from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.dependencies import get_current_user

from app.models import User, Paper
from app.schemas.user import (
    UserProfile, PublicUserProfile, PasswordChange
)

from app.services.auth import verify_password, get_password_hash
from app.services.stats import update_user_stats

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfile)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    paper_count = db.query(func.count(Paper.id)).filter(
        Paper.author_id == current_user.id,
        Paper.is_published
    ).scalar()

    profile = UserProfile.model_validate(current_user)
    profile.paper_count = paper_count

    return profile


@router.post("/me/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(password_data.current_password, current_user.password):  # noqa
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )

    current_user.password = get_password_hash(password_data.new_password)
    db.commit()

    return {"detail": "password changed"}


@router.get("/{username}", response_model=PublicUserProfile)
async def get_user_profile(
    username: str,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found",
        )

    update_user_stats(db, user.id)
    db.refresh(user)

    return PublicUserProfile.model_validate(user)
