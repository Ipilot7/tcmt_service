import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Task
from apps.core.notifications import send_push_notification, notify_managers

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Task)
def task_notification_handler(sender, instance, created, **kwargs):
    resp_person = instance.responsible_person
    logger.info(f"--- Task Signal [{instance.task_number}] ---")
    logger.info(f"Created: {created}, Status: {instance.status}, Responsible: {resp_person}")
    
    if created:
        if resp_person:
            logger.info(f"NOTIFYING NEW TASK: user {resp_person.id}")
            send_push_notification(
                user=resp_person,
                title="🆕 Новая задача назначена",
                body=f"Вам назначена задача № {instance.task_number}: {instance.description[:100]}",
                data={"type": "new_task", "task_id": str(instance.id)}
            )
    else:
        # If it was an update, notify the responsible person (if any)
        if resp_person and instance.status != 'CP':
            logger.info(f"NOTIFYING UPDATE: user {resp_person.id}")
            send_push_notification(
                user=resp_person,
                title="🔄 Обновление по задаче",
                body=f"Задача № {instance.task_number} была обновлена. Текущий статус: {instance.get_status_display()}",
                data={"type": "task_updated", "task_id": str(instance.id)}
            )
        
        # Notify managers about the update
        notify_managers(
            title="📢 Обновление в системе",
            body=f"Задача {instance.task_number} изменена (Статус: {instance.get_status_display()})",
            data={"type": "manager_info", "task_id": str(instance.id)}
        )
