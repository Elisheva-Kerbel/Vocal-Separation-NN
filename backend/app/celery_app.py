"""Celery application (Phase 5)."""

import numpy as np
from celery import Celery
from celery.signals import worker_process_init

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


@worker_process_init.connect
def _warm_up(**_kwargs):
    """Pre-warm librosa/numba JIT and audio IO on worker start."""
    from ai import audio_io
    audio_io.stft(np.zeros(22050, dtype="float32"))
