from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.routers import router

app = FastAPI(
    title=settings.name,
    docs_url="/api/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # todo: specify cors in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount(
        "/static", StaticFiles(directory=str(frontend_path)), name="static"
    )


@app.get("/")
def serve_frontend():
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
