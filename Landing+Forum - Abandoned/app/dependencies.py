from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

from app.services.auth import decode_access_token

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    if credentials is None:
        raise credentials_exception

    token_data = decode_access_token(credentials.credentials)

    if token_data is None or token_data.user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == token_data.user_id).first()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user account is deactivated",
        )

    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if credentials is None:
        return None

    token_data = decode_access_token(credentials.credentials)

    if token_data is None or token_data.user_id is None:
        return None

    user = db.query(User).filter(User.id == token_data.user_id).first()

    if user is None or not user.is_active:
        return None

    return user


class Pagination:
    def __init__(
        self,
        page: int = 1,
        page_size: int = 20,
    ):
        from app.config import settings

        self.page = max(1, page)
        self.page_size = min(max(1, page_size), settings.max_page_size)
        self.offset = (self.page - 1) * self.page_size
