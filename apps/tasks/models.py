from django.db import models
from apps.locations.models import Hospital
from apps.devices.models import DeviceType
from apps.accounts.models import User
from apps.core.choices import StatusChoices

class Task(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='tasks')
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE, related_name='tasks')
    task_number = models.CharField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    status = models.CharField(
        max_length=2,
        choices=StatusChoices.choices,
        default=StatusChoices.NEW,
        db_index=True
    )
    responsible_person = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='responsible_tasks',
        limit_choices_to={'is_superuser': False},
        null=True,
        blank=True
    )
    created_at = models.DateField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'tasks'
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.task_number:
            from django.utils import timezone
            year = timezone.now().strftime('%y')
            # Look for the last task of the current year
            last_task = Task.objects.filter(task_number__startswith=f'SR-{year}-').order_by('-task_number').first()
            if last_task:
                try:
                    last_number = int(last_task.task_number.split('-')[-1])
                    new_number = last_number + 1
                except (ValueError, IndexError):
                    new_number = 1
            else:
                new_number = 1
            self.task_number = f'SR-{year}-{new_number:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Task {self.task_number} - {self.get_status_display()}"
