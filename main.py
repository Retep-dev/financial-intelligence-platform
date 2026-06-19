from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routes.document_routes import router as document_router
from api.routes.health import router as health_router
from db.qdrant.collections import ensure_collection_exists, validate_collection


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_collection_exists()

    if not validate_collection():
        raise RuntimeError(
            "Qdrant collection vector size does not match configured embedding dimensions. "
            "Delete the collection or update EMBEDDING_DIMENSIONS."
        )

    yield


app = FastAPI(
    title="Financial Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(health_router)
app.include_router(document_router)


@app.get("/")
def root():
    return {
        "status": "running",
        "service": "financial-intelligence-platform"
    }
