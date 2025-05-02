from celery import Celery
from config import settings

celery_app = Celery(
    "ai_vibe_refresh",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json']
)

import app.tasks.ai_vibe