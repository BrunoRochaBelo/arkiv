"""Celery application with optional Redis fallback."""
import os
from celery import Celery
from .config import config_by_name
try:
    from redis import Redis  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Redis = None

celery_app = Celery(__name__)


def init_celery(config_name: str = "development") -> Celery:
    """Initialize Celery and fall back to in-memory if Redis is unavailable."""
    config = config_by_name[config_name]
    broker = getattr(config, "CELERY_BROKER_URL", "redis://localhost:6379/0")
    backend = getattr(config, "CELERY_RESULT_BACKEND", broker)

    celery_app.conf.broker_url = broker
    celery_app.conf.result_backend = backend

    eager = getattr(config, "CELERY_TASK_ALWAYS_EAGER", False)
    if not eager and broker.startswith("redis"):
        try:
            if Redis is None:
                raise RuntimeError("redis lib missing")
            Redis.from_url(broker).ping()
        except Exception:
            eager = True
    if eager:
        celery_app.conf.broker_url = "memory://"
        celery_app.conf.result_backend = "cache+memory://"
        celery_app.conf.task_always_eager = True

    return celery_app


init_celery(os.getenv("FLASK_ENV", "development"))
