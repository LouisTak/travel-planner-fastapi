from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    xai_api_key: str
    env: str = "development"
    redis_host: str = "redis"
    redis_port: int = 6379
    cache_ttl: int = 3600  # 1 hour in seconds
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
