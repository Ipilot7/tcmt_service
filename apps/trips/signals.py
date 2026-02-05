from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Trip
from apps.core.notifications import send_push_notification

@receiver(post_save, sender=Trip)
def trip_notification_handler(sender, instance, created, **kwargs):
    if created:
        # Notify the responsible person about the new trip
        if instance.responsible_person:
            send_push_notification(
                user=instance.responsible_person,
                title="Новая поездка назначена",
                body=f"Вам назначена поездка {instance.task_number}: {instance.description[:50]}...",
                data={
                    "type": "new_trip",
                    "trip_id": str(instance.id),
                    "task_number": instance.task_number
                }
            )
