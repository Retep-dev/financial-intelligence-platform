from qdrant_client import QdrantClient

from core.config.settings import settings


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(url=settings.QDRANT_URL)
