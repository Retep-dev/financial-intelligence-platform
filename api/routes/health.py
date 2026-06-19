from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.dependencies.db import get_db
from db.qdrant.client import get_qdrant_client
from db.qdrant.collections import validate_collection, COLLECTION_NAME
from db.qdrant.metrics import get_collection_stats

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)


@router.get("")
def health_check():
    return {
        "status": "healthy",
        "service": "financial-intelligence-platform"
    }


@router.get("/db")
def health_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "component": "postgresql"
        }
    except Exception as exc:
        return {
            "status": "unhealthy",
            "component": "postgresql",
            "detail": str(exc)
        }


@router.get("/qdrant")
def health_qdrant():
    try:
        client = get_qdrant_client()
        client.get_collections()

        collection_valid = validate_collection()

        return {
            "status": "healthy" if collection_valid else "degraded",
            "component": "qdrant",
            "collection": COLLECTION_NAME,
            "collection_valid": collection_valid
        }
    except Exception as exc:
        return {
            "status": "unhealthy",
            "component": "qdrant",
            "detail": str(exc)
        }


@router.get("/metrics")
def metrics():
    try:
        stats = get_collection_stats()
        return {
            "status": "healthy",
            "qdrant": stats
        }
    except Exception as exc:
        return {
            "status": "unhealthy",
            "detail": str(exc)
        }
