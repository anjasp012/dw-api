from fastapi import APIRouter, Depends
from app.api.v1.endpoints import auth, wishes, admin
from app.api.v1.deps import verify_unity_api_key

api_router = APIRouter()

# 🔐 Authentication (Login, Refresh Token, Profile)
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# 🖥️ Dream Wall / Unity (Membutuhkan header X-API-Key dari .env)
api_router.include_router(
    wishes.router,
    prefix="/wishes",
    tags=["Dream Wall (Public)"],
    dependencies=[Depends(verify_unity_api_key)]
)

# ⚙️ Admin CMS (Membutuhkan JWT Bearer Token)
api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["Admin CMS"]
)