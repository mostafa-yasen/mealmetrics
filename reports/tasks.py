from celery import shared_task


@shared_task
def debug_celery_task():
    print("Celery is working!")
    return "Success"
