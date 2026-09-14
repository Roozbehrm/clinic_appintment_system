from celery import shared_task

from .services import delete_expired_free_slots


@shared_task
def cleanup_expired_free_slots():
    return delete_expired_free_slots()
