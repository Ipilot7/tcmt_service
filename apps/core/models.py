import datetime
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class Region(models.Model):
    name = models.CharField(_('Name'), max_length=100)

    def __str__(self):
        return self.name


class Institution(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name=_('Region'))
    sale_date = models.DateField(_('Sale Date'), null=True, blank=True)
    equipments = models.ManyToManyField(
        'Equipment', 
        blank=True, 
        related_name='institutions',
        verbose_name=_('Equipments')
    )

    @property
    def warranty_end(self):
        if self.sale_date:
            try:
                return self.sale_date.replace(year=self.sale_date.year + 2)
            except ValueError:
                # Handle Feb 29th
                return self.sale_date + (datetime.date(self.sale_date.year + 2, 1, 1) - datetime.date(self.sale_date.year, 1, 1))
        return None

    @property
    def is_under_warranty(self):
        if not self.sale_date:
            return False
        return timezone.now().date() <= self.warranty_end

    def __str__(self):
        return self.name


class EquipmentType(models.Model):
    name = models.CharField(_('Name'), max_length=255)

    def __str__(self):
        return self.name


class Status(models.Model):
    class Name(models.TextChoices):
        INITIAL = 'initial', _('Initial')
        IN_PROGRESS = 'in_progress', _('In Progress')
        SUCCESS = 'success', _('Success')
        CANCELED = 'canceled', _('Canceled')

    name = models.CharField(
        _('Name'), 
        max_length=20, 
        choices=Name.choices, 
        default=Name.INITIAL,
        unique=True
    )

    def __str__(self):
        return self.get_name_display()


class Equipment(models.Model):
    equipment_type = models.ForeignKey(
        EquipmentType, 
        on_delete=models.PROTECT, 
        related_name='equipment_instances',
        verbose_name=_('Equipment Type')
    )
    serial_number = models.CharField(_('Serial Number'), max_length=100, unique=True)

    def __str__(self):
        return f"{self.equipment_type.name} ({self.serial_number})"
