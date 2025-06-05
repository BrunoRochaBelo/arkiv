"""Simple Celery application configured with Redis."""
from celery import Celery
from .config import config_by_name

celery_app = Celery(__name__)


def init_celery(config_name: str = "development") -> Celery:
    """Initialize Celery with broker and backend from config."""
    config = config_by_name[config_name]
    celery_app.conf.broker_url = getattr(config, "CELERY_BROKER_URL", "redis://localhost:6379/0")
    celery_app.conf.result_backend = getattr(config, "CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    return celery_app


init_celery()
