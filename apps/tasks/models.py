from django.db import models
from apps.locations.models import Hospital
from apps.devices.models import DeviceType
from apps.core.models import Status
from apps.accounts.models import User

class Task(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='tasks')
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE, related_name='tasks')
    task_number = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    created_at = models.DateField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'tasks'
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['-created_at']

    def __str__(self):
        return self.task_number

class TaskStatus(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='statuses')
    status = models.ForeignKey(Status, on_delete=models.PROTECT, related_name='task_statuses')
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'task_statuses'
        unique_together = ('task', 'changed_at')
        verbose_name = 'Task Status'
        verbose_name_plural = 'Task Statuses'
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.task.task_number} - {self.status.name}"

class TaskResponsible(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='responsibles')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks_assigned')

    class Meta:
        db_table = 'task_responsibles'
        unique_together = ('task', 'user')
        verbose_name = 'Task Responsible'
        verbose_name_plural = 'Task Responsibles'

    def __str__(self):
        return f"{self.task.task_number} - {self.user.fullname}"
