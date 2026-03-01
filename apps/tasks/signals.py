import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Task
from apps.core.notifications import send_push_notification, notify_managers

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Task)
def task_notification_handler(sender, instance, created, **kwargs):
    logger.info(f"Signal triggered for Task {instance.task_number}. Created: {created}")
    
    if created:
        if instance.responsible_person:
            logger.info(f"Notifying responsible person {instance.responsible_person.id} about NEW task")
            send_push_notification(
                user=instance.responsible_person,
                title="🆕 Новая задача назначена",
                body=f"Вам назначена задача № {instance.task_number}: {instance.description[:100]}",
                data={"type": "new_task", "task_id": str(instance.id)}
            )
    else:
        # При обновлении задачи уведомляем ответственного, если статус не завершен
        if instance.responsible_person and instance.status != 'CP':
             send_push_notification(
                user=instance.responsible_person,
                title="🔄 Обновление по задаче",
                body=f"Задача № {instance.task_number} была обновлена. Текущий статус: {instance.get_status_display()}",
                data={"type": "task_updated", "task_id": str(instance.id)}
            )
        
        # Уведомляем менеджеров
        notify_managers(
            title="📢 Обновление задачи",
            body=f"Задача {instance.task_number} изменена. Статус: {instance.get_status_display()}",
            data={"type": "task_updated_manager", "task_id": str(instance.id)}
        )
