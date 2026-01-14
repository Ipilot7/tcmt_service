import datetime
from django.db import models
from django.conf import settings
from apps.core.models import Region, Institution, EquipmentType, Status

class Request(models.Model):
    created_at = models.DateField(default=datetime.date.today)

    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='requests'
    )

    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    institution = models.ForeignKey(Institution, on_delete=models.PROTECT)

    description = models.TextField()
    contact_phone = models.CharField(max_length=20)

    request_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    equipment_type = models.ForeignKey(EquipmentType, on_delete=models.PROTECT)
    status = models.ForeignKey(Status, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        if not self.request_number:
            year = str(self.created_at.year)[-2:]
            # Count existing requests for this year
            count = Request.objects.filter(request_number__startswith=f"SR-{year}").count() + 1
            self.request_number = f"SR-{year}-{count:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.request_number
