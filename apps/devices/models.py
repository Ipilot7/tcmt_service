from django.db import models
from apps.locations.models import Hospital

class DeviceType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'device_types'
        verbose_name = 'Device Type'
        verbose_name_plural = 'Device Types'
        ordering = ['name']

    def __str__(self):
        return self.name

class Device(models.Model):
    serial_number = models.CharField(max_length=255, unique=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='devices', null=True, blank=True)
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE, related_name='devices')

    class Meta:
        db_table = 'devices'
        verbose_name = 'Device'
        verbose_name_plural = 'Devices'
        ordering = ['serial_number']

    def __str__(self):
        return self.serial_number
