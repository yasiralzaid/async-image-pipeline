import os
import time
from celery import Celery

# get broker and backend from environment variables
broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
backend_url = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# initialize celery app
celery_app = Celery(
    "tasks",
    broker=broker_url,
    backend=backend_url
)

@celery_app.task
def process_image_task(filename: str):
    # simulate processing delay for day 1
    time.sleep(5)
    return {"status": "completed", "filename": filename}