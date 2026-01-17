from django.db import models
from django.utils.translation import gettext_lazy as _

class Region(models.Model):
    name = models.CharField(_('Name'), max_length=100)

    def __str__(self):
        return self.name


class Institution(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name=_('Region'))

    def __str__(self):
        return self.name


class EquipmentType(models.Model):
    name = models.CharField(_('Name'), max_length=255)

    def __str__(self):
        return self.name


class Status(models.Model):
    name = models.CharField(_('Name'), max_length=100)

    def __str__(self):
        return self.name

