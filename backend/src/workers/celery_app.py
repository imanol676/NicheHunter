import os
from celery import Celery

# Conectamos Celery a la instancia de Redis que corre en tu Docker
redis_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "nichehunter_worker",
    broker=redis_url,
    backend=redis_url,
    include=["src.workers.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
