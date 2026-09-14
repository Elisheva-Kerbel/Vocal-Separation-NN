"""VocalSplit backend — FastAPI application."""

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session as DbSession

from app.auth import current_user, get_db
from app.db.models import User
from app.quotas import get_usage_info

from app.admin import router as admin_router
from app.auth import router as auth_router
from app.config import SERVICE_NAME
from app.coupons import router as coupons_router
from app.demo import router as demo_router
from app.library import router as library_router
from app.public import router as public_router
from app.settings_routes import router as settings_router
from app.songs import router as songs_router
from app.subscriptions import router as subscriptions_router
from app.upload import router as upload_router

app = FastAPI(title="VocalSplit Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(demo_router)
app.include_router(auth_router)
app.include_router(upload_router)
app.include_router(songs_router)
app.include_router(library_router)
app.include_router(public_router)
app.include_router(coupons_router)
app.include_router(admin_router)
app.include_router(settings_router)
app.include_router(subscriptions_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/quota")
def quota_info(
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
):
    return get_usage_info(db, user)
