from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.dependencies.db import get_db
from db.qdrant.client import get_qdrant_client

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
        return {
            "status": "healthy",
            "component": "qdrant"
        }
    except Exception as exc:
        return {
            "status": "unhealthy",
            "component": "qdrant",
            "detail": str(exc)
        }
