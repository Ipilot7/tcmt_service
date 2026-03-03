import logging
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Task
from apps.core.notifications import send_push_notification, notify_managers

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Task)
def task_notification_handler(sender, instance, created, **kwargs):
    logger.info(f"--- Task Signal (post_save) [{instance.task_number}] ---")
    
    if created:
        # Notify managers only about NEW tasks
        notify_managers(
            title="🆕 Новая задача",
            body=f"Создана задача {instance.task_number}: {instance.description[:100]}",
            data={"type": "manager_info", "task_id": str(instance.id)}
        )
    else:
        # Notify ONLY assigned users about status updates
        users = instance.responsible_persons.all()
        for user in users:
            send_push_notification(
                user=user,
                title="📢 Обновление задачи",
                body=f"В задаче {instance.task_number} изменился статус на {instance.get_status_display()}",
                data={"type": "task_update", "task_id": str(instance.id)}
            )

@receiver(m2m_changed, sender=Task.responsible_persons.through)
def task_m2m_notification_handler(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        logger.info(f"--- Task M2M changed (post_add) [{instance.task_number}] ---")
        from apps.accounts.models import User
        users = User.objects.filter(pk__in=pk_set)
        for user in users:
            logger.info(f"NOTIFYING ASSIGNED USER: {user.id}")
            send_push_notification(
                user=user,
                title="🆕 Вам назначена задача",
                body=f"Вы добавлены в задачу № {instance.task_number}: {instance.description[:100]}",
                data={"type": "new_task", "task_id": str(instance.id)}
            )
