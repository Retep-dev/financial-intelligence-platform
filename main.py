from fastapi import FastAPI

from api.routes.document_routes import router as document_router
from api.routes.health import router as health_router

app = FastAPI(
    title="Financial Intelligence Platform",
    version="1.0.0"
)

app.include_router(health_router)
app.include_router(document_router)


@app.get("/")
def root():
    return {
        "status": "running",
        "service": "financial-intelligence-platform"
    }
