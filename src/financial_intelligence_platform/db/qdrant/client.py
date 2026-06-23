from qdrant_client import QdrantClient

from financial_intelligence_platform.core.config.settings import settings


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(url=settings.QDRANT_URL)
