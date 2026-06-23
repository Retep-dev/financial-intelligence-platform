from financial_intelligence_platform.workers.celery_app import celery_app


if __name__ == "__main__":
    celery_app.worker_main([
        "worker",
        "--loglevel=info",
        "--queues=celery",
        "--concurrency=2"
    ])
