from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Workflow Builder"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api"

    # MySQL
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "123456"
    MYSQL_DB: str = "AiWork"

    # JWT
    SECRET_KEY: str = "your-secret-key-keep-it-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # 百炼 / DashScope (OpenAI 兼容)
    DASHSCOPE_API_KEY: str = "sk-...."
    DASHSCOPE_BASE_URL: str = "model"
    DASHSCOPE_MODEL: str = "qwen3.7-plus"

    # File upload
    UPLOAD_DIR: str = "uploads"

    class Config:
        case_sensitive = True


settings = Settings()