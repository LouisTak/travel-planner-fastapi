from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    xai_api_key: str
    env: str = "development"
    redis_host: str = "redis"
    redis_port: int = 6379
    cache_ttl: int = 3600  # 1 hour in seconds
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "travel-note"
    database_url: str = f"postgresql://{postgres_user}:{postgres_password}@db:5432/{postgres_db}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
