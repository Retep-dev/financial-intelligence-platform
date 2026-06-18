from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Financial Intelligence Platform"

    DATABASE_URL: str
    REDIS_URL: str

    class Config:
        env_file = ".env"


settings = Settings()
