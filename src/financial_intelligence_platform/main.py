from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

from financial_intelligence_platform.api.routes.document_routes import router as document_router
from financial_intelligence_platform.api.routes.health import router as health_router
from financial_intelligence_platform.api.routes.queries import router as query_router
from financial_intelligence_platform.db.qdrant.collections import ensure_collection_exists, validate_collection


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
app.include_router(query_router)

frontend_dir = Path(__file__).parent.parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/")
def root():
    return {
        "status": "running",
        "service": "financial-intelligence-platform"
    }


@app.get("/app")
def serve_app():
    return FileResponse(frontend_dir / "index.html")
