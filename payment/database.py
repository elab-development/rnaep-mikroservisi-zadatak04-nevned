from pydantic_settings import BaseSettings, SettingsConfigDict
from redis_om import get_redis_connection

class Settings(BaseSettings):
    
    app_redis_host: str = "localhost"
    app_redis_port: int = 6379
    app_redis_password: str = ""
    inventory_url: str = "http://localhost:8000"

    
    model_config = SettingsConfigDict(
        env_file=".env", 
        extra="ignore",
        env_prefix=""
    )

settings = Settings()

redis = get_redis_connection(
    host=settings.app_redis_host,
    port=settings.app_redis_port,
    password=settings.app_redis_password,
    decode_responses=True
)