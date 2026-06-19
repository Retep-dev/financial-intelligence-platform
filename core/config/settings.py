from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Financial Intelligence Platform"

    DATABASE_URL: str
    REDIS_URL: str
    QDRANT_URL: str = "http://localhost:6333"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
