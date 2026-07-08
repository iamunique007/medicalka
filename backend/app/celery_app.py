from celery import Celery

from app.config import (
    CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND,
    CLEANUP_INTERVAL_SECONDS,
)

celery_app = Celery(
    "medicalka",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.tasks"],
)

celery_app.conf.timezone = "UTC"

celery_app.conf.beat_schedule = {
    "cleanup-expired-unverified-users": {
        "task": "app.tasks.cleanup_expired_unverified_users",
        "schedule": CLEANUP_INTERVAL_SECONDS,
    },
}