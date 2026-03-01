import logging
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Trip
from apps.core.notifications import send_push_notification

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Trip)
def trip_notification_handler(sender, instance, created, **kwargs):
    logger.info(f"--- Trip Signal (post_save) [{instance.task_number}] ---")

@receiver(m2m_changed, sender=Trip.responsible_persons.through)
def trip_m2m_notification_handler(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        logger.info(f"--- Trip M2M changed (post_add) [{instance.task_number}] ---")
        from apps.accounts.models import User
        users = User.objects.filter(pk__in=pk_set)
        for user in users:
            logger.info(f"NOTIFYING ASSIGNED USER (Trip): {user.id}")
            send_push_notification(
                user=user,
                title="🆕 Вам назначена поездка",
                body=f"Вы добавлены в поездку № {instance.task_number}: {instance.description[:100]}",
                data={"type": "new_trip", "trip_id": str(instance.id)}
            )
