import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Dream Wall API")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password123@localhost:5432/dreamwall_db"
    )
    SECRET_KEY: str = os.getenv("SECRET_KEY", "kunci_rahasia_jwt_super_aman")
    UNITY_API_KEY: str = os.getenv("UNITY_API_KEY", "dreamwall_local_secret_2026")
    JWT_EXPIRE_SECONDS: int = 3600
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 7 * 24 * 3600


settings = Settings()