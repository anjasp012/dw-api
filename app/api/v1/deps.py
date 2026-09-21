from typing import Optional
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.core.security import decode_token

# 🔐 CMS Admin Bearer JWT Scheme
cms_bearer_scheme = HTTPBearer(
    auto_error=False,
    description="Masukkan JWT Token (didapatkan dari POST /api/v1/auth/login)"
)

# 🖥️ Dream Wall Access Token Header (from .env)
wall_token_header = APIKeyHeader(
    name="X-Access-Token",
    auto_error=False
)

unity_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False
)


def verify_wall_access_token(
    access_token: Optional[str] = Security(wall_token_header),
    api_key: Optional[str] = Security(unity_key_header)
) -> str:
    """
    Validasi header X-Access-Token untuk semua request Layar Dream Wall / Unity.
    Nilai harus cocok dengan ACCESS_TOKEN di file .env.
    """
    client_token = access_token or api_key
    if not client_token or client_token != settings.ACCESS_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Akses ditolak: Header 'X-Access-Token' tidak valid atau tidak disertakan."
        )
    return client_token


# Alias fungsi untuk kompatibilitas
verify_unity_api_key = verify_wall_access_token


def get_current_admin(
    auth_header: Optional[HTTPAuthorizationCredentials] = Security(cms_bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Autentikasi CMS Admin murni menggunakan JWT Bearer Token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized. Token JWT tidak valid atau telah kadaluarsa",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not auth_header or not auth_header.credentials:
        raise credentials_exception

    token = auth_header.credentials
    payload = decode_token(token, expected_type="access")
    if not payload:
        raise credentials_exception

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()

    if user is None:
        raise credentials_exception
    if getattr(user, "is_active", 1) != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun administrator dinonaktifkan"
        )
    return user