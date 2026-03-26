from django.db import models
from apps.locations.models import Hospital
from apps.devices.models import DeviceType
from apps.accounts.models import User
from apps.core.choices import StatusChoices

class Trip(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='trips', null=True, blank=True)
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE, related_name='trips', null=True, blank=True)
    task_number = models.CharField(max_length=255, db_index=True, blank=True)
    description = models.TextField()
    contact_phone = models.CharField(max_length=20, null=True, blank=True)
    trip_date = models.DateField(null=True, blank=True)
    order_number = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(
        max_length=2,
        choices=StatusChoices.choices,
        default=StatusChoices.NEW,
        db_index=True
    )
    responsible_persons = models.ManyToManyField(
        User,
        related_name='responsible_trips',
        limit_choices_to={'is_superuser': False},
        blank=True,
        verbose_name='Responsible Persons'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'trips'
        verbose_name = 'Trip'
        verbose_name_plural = 'Trips'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.task_number:
            from django.utils import timezone
            year = timezone.now().strftime('%y')
            # Look for the last trip of the current year
            last_trip = Trip.objects.filter(task_number__startswith=f'SR-{year}-').order_by('-task_number').first()
            if last_trip:
                try:
                    last_number = int(last_trip.task_number.split('-')[-1])
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
        return f"Trip {self.task_number} - {self.get_status_display()}"

class TripResult(models.Model):
    trip = models.OneToOneField(Trip, on_delete=models.CASCADE, primary_key=True, related_name='result')
    result_info = models.TextField()

    class Meta:
        db_table = 'trip_results'
        verbose_name = 'Trip Result'
        verbose_name_plural = 'Trip Results'

    def __str__(self):
        return f"Result for Trip {self.trip_id}"
