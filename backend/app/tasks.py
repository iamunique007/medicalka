from sqlalchemy import delete

from app.models import User
from app.celery_app import celery_app
from app.db import SyncSessionLocal
from app.config import UNVERIFIED_USER_TTL_MIN

from datetime import datetime, timedelta, timezone


@celery_app.task(name="app.tasks.cleanup_expired_unverified_users")
def cleanup_expired_unverified_users() -> int:
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
        minutes=UNVERIFIED_USER_TTL_MIN
    )

    with SyncSessionLocal() as session:
        result = session.execute(
            delete(User).where(
                User.is_verified.is_(False),
                User.created_at < cutoff,
            )
        )
        session.commit()

    deleted = result.rowcount

    return deleted