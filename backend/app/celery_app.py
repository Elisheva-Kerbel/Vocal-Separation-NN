"""Celery application (Phase 5)."""

from celery import Celery

from app.config import load_settings

settings = load_settings()

celery = Celery(
    "stemspace",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    task_default_queue="separation",
)

celery.autodiscover_tasks(["app"])
