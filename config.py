from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    xai_api_key: str
    env: str = "development"
    redis_host: str = "redis"
    redis_port: int = 6379
    cache_ttl: int = 3600  # 1 hour in seconds
    db_host: str = "postgres"
    db_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "travel-note"
    DATABASE_URL: str = f"postgresql+psycopg2://{postgres_user}:{postgres_password}@localhost:5432/{postgres_db}"
    algorithm: str = "HS256"
    secret_key: str
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Set environment to test if running tests
if os.environ.get("TESTING") == "1":
    settings = Settings(env="test")
else:
    settings = Settings()
