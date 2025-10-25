"""
Celeryアプリケーション設定
"""
from celery import Celery
from config.settings import settings

# Celeryアプリケーション
celery_app = Celery(
    "document_automation",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks", "app.workers.rag_tasks"]
)

# Celery設定
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Tokyo",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30分
    task_soft_time_limit=1500,  # 25分
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

