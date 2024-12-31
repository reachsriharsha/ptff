from celery import Celery
import os
from dotenv import load_dotenv
load_dotenv()


broker_url = os.environ.get('CELERY_BROKER_URL')
result_backend = os.environ.get('CELERY_RESULT_BACKEND')

celery_app = Celery(
    'tasks',
    broker=broker_url,
    backend=result_backend,
)

celery_app.conf.update (
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata', #can be UTC
    enable_utc=True,
)

