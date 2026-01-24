from django.db import models
from apps.locations.models import Hospital
from apps.devices.models import DeviceType
from apps.core.models import Status
from apps.accounts.models import User

class Trip(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='trips')
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE, related_name='trips')
    task_number = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    contact_phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'trips'
        verbose_name = 'Trip'
        verbose_name_plural = 'Trips'
        ordering = ['-created_at']

    def __str__(self):
        return f"Trip {self.id} - {self.task_number}"

class TripStatus(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='statuses')
    status = models.ForeignKey(Status, on_delete=models.PROTECT, related_name='trip_statuses')
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'trip_statuses'
        unique_together = ('trip', 'changed_at')
        verbose_name = 'Trip Status'
        verbose_name_plural = 'Trip Statuses'
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.trip.task_number} - {self.status.name}"

class TripResult(models.Model):
    trip = models.OneToOneField(Trip, on_delete=models.CASCADE, primary_key=True, related_name='result')
    result_info = models.TextField()

    class Meta:
        db_table = 'trip_results'
        verbose_name = 'Trip Result'
        verbose_name_plural = 'Trip Results'

    def __str__(self):
        return f"Result for Trip {self.trip_id}"

class TripUser(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='users')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips')

    class Meta:
        db_table = 'trip_users'
        unique_together = ('trip', 'user')
        verbose_name = 'Trip User'
        verbose_name_plural = 'Trip Users'

    def __str__(self):
        return f"Trip {self.trip_id} - {self.user.fullname}"
