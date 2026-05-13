from fastapi import APIRouter

from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.papers import router as papers_router
from app.routers.votes import router as votes_router

router = APIRouter(prefix="/api")

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(papers_router)
router.include_router(votes_router)
