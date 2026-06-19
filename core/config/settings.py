from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Financial Intelligence Platform"

    DATABASE_URL: str
    REDIS_URL: str
    QDRANT_URL: str = "http://localhost:6333"

    # Embedding provider: "openai" or "nvidia"
    EMBEDDING_PROVIDER: str = "nvidia"

    # OpenAI settings
    OPENAI_API_KEY: str | None = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"

    # NVIDIA NIM settings
    NVIDIA_API_KEY: str | None = None
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_EMBEDDING_MODEL: str = "nvidia/nv-embedqa-e5-v5"

    EMBEDDING_DIMENSIONS: int = 1024

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
