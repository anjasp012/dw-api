import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Dream Wall API")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password123@localhost:5432/dreamwall_db"
    )
    SECRET_KEY: str = os.getenv("SECRET_KEY", "8dad95a3d7d2ecc565f7a092cf48fb4f0f0f430731d24440e4dd01c9d6a8c7f0")
    ACCESS_TOKEN: str = os.getenv("ACCESS_TOKEN", os.getenv("UNITY_API_KEY", "60d0b738cf14cb743aa277b92217f6568bb54c2a4795d35b543ce8e0b92ebfb6"))
    UNITY_API_KEY: str = ACCESS_TOKEN
    JWT_EXPIRE_SECONDS: int = 3600
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 7 * 24 * 3600


settings = Settings()