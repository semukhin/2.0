from celery import Celery
from src.core.config import settings

celery_app = Celery(
    "lawgpt_v2",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.task_routes = {  # Пример маршрутизации задач
    # 'src.tasks.example_task': {'queue': 'default'},
}
