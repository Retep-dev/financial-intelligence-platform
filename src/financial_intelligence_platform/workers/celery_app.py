from celery import Celery

from financial_intelligence_platform.core.config.settings import settings

celery_app = Celery(
    "financial_intelligence",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["financial_intelligence_platform.workers.tasks.document_processing"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,
    worker_prefetch_multiplier=1
)
