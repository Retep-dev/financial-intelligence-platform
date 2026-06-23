from openai import OpenAI

from financial_intelligence_platform.core.config.settings import settings


def get_embedding_client() -> OpenAI:
    """Return an OpenAI-compatible client for the configured embedding provider."""
    provider = settings.EMBEDDING_PROVIDER.lower()

    if provider == "openai":
        return OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )

    if provider == "nvidia":
        return OpenAI(
            api_key=settings.NVIDIA_API_KEY,
            base_url=settings.NVIDIA_BASE_URL
        )

    raise ValueError(f"Unsupported embedding provider: {settings.EMBEDDING_PROVIDER}")


def get_embedding_model() -> str:
    provider = settings.EMBEDDING_PROVIDER.lower()

    if provider == "openai":
        return settings.OPENAI_EMBEDDING_MODEL

    if provider == "nvidia":
        return settings.NVIDIA_EMBEDDING_MODEL

    raise ValueError(f"Unsupported embedding provider: {settings.EMBEDDING_PROVIDER}")


def get_embedding_dimensions() -> int:
    return settings.EMBEDDING_DIMENSIONS
