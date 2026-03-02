from django.db import models
from apps.locations.models import Hospital
from apps.devices.models import DeviceType
from apps.accounts.models import User
from apps.core.choices import StatusChoices

class TaskCategory(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название категории")

    class Meta:
        verbose_name = "Категория заявки"
        verbose_name_plural = "Категории заявок"

    def __str__(self):
        return self.name

class Task(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='tasks')
    category = models.ForeignKey(TaskCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks', verbose_name="К чему относится")
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE, related_name='tasks')
    task_number = models.CharField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Номер телефона")
    status = models.CharField(
        max_length=2,
        choices=StatusChoices.choices,
        default=StatusChoices.NEW,
        db_index=True
    )
    responsible_persons = models.ManyToManyField(
        User,
        related_name='responsible_tasks',
        limit_choices_to={'is_superuser': False},
        blank=True,
        verbose_name='Responsible Persons'
    )
    task_date = models.DateField(null=True, blank=True)
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

    @property
    def responsible_persons_names(self):
        return ", ".join([u.fullname for u in self.responsible_persons.all()]) or "None"

    @property
    def responsible_persons_ids(self):
        return ", ".join([str(u.id) for u in self.responsible_persons.all()]) or "None"

    def __str__(self):
        return f"Task {self.task_number} - {self.get_status_display()}"
