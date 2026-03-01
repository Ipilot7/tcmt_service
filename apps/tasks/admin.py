from django.contrib import admin, messages
from .models import Task
from apps.core.notifications import send_push_notification

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_number', 'hospital', 'device_type', 'status', 'get_responsible_persons', 'task_date', 'created_at')
    list_filter = ('status', 'hospital', 'device_type', 'responsible_persons', 'task_date', 'created_at')
    search_fields = ('task_number', 'description')
    actions = ['send_notification']

    def get_responsible_persons(self, obj):
        return ", ".join([user.fullname for user in obj.responsible_persons.all()])
    get_responsible_persons.short_description = 'Responsible Persons'

    @admin.action(description="Отправить повторное уведомление всем ответственным")
    def send_notification(self, request, queryset):
        sent_count = 0
        for task in queryset:
            for person in task.responsible_persons.all():
                send_push_notification(
                    user=person,
                    title="Напоминание о задаче",
                    body=f"Напоминание по задаче {task.task_number}: {task.description[:50]}...",
                    data={"task_id": str(task.id), "type": "task_reminder"}
                )
                sent_count += 1
        self.message_user(request, f"Отправлено {sent_count} уведомлений заинтересованным лицам.", messages.SUCCESS)
