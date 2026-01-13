import datetime
from django.db import models
from django.conf import settings
from apps.core.models import Region, Institution, EquipmentType, Status

class Trip(models.Model):
    created_at = models.DateField(default=datetime.date.today)

    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='trips'
    )

    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    institution = models.ForeignKey(Institution, on_delete=models.PROTECT)

    description = models.TextField()
    contact_phone = models.CharField(max_length=20)

    request_number = models.CharField(max_length=20)

    equipment_type = models.ForeignKey(EquipmentType, on_delete=models.PROTECT)
    status = models.ForeignKey(Status, on_delete=models.PROTECT)

    escort_name = models.CharField(max_length=255)
    escort_phone = models.CharField(max_length=20)

    order_number = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    result_info = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.request_number:
            import datetime
            today = datetime.date.today()
            year = str(today.year)[-2:]
            # Count existing trips for this year
            count = Trip.objects.filter(request_number__startswith=f"SR-{year}").count() + 1
            self.request_number = f"SR-{year}-{count:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Trip {self.request_number}"
