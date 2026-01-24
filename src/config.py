from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    supabase_service_key: str
    database_url: str
    environment: str = "development"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()