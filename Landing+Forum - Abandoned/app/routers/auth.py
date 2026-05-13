from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user

from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token

from app.services.auth import (
    verify_password, get_password_hash, create_access_token
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(
        User.username == user_data.username
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username already registered",
        )

    existing_email = db.query(User).filter(
        User.email == user_data.email
    ).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="email already registered",
        )

    hashed_password = get_password_hash(user_data.password)

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(
        data={"user_id": new_user.id, "username": new_user.username}
    )

    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(new_user),
    )


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(
        (User.username == form_data.username) |
        (User.email == form_data.username)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect username or password",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect username or password",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user account is deactivated",
        )

    user.last_login = datetime.now(timezone.utc)
    db.commit()

    access_token = create_access_token(
        data={"user_id": user.id, "username": user.username}
    )

    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    return UserResponse.model_validate(current_user)
