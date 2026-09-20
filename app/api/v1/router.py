from fastapi import APIRouter, Depends
from app.api.v1.endpoints import wishes, auth, admin
from app.api.v1.deps import verify_unity_api_key

api_router = APIRouter()

# 🖥️ Unity / Layar Dream Wall (Membutuhkan header X-API-Key dari .env)
api_router.include_router(
    wishes.router,
    prefix="/wishes",
    tags=["Wishes / Unity"],
    dependencies=[Depends(verify_unity_api_key)]
)

# 🔐 Authentication CMS (Login, Refresh Token, Profile)
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Auth CMS"]
)

# ⚙️ Admin CMS (Membutuhkan JWT Bearer Token)
api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["Admin / CMS"]
)