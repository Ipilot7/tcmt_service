from django.db import models

class Status(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'statuses'
        verbose_name = 'Status'
        verbose_name_plural = 'Statuses'
        ordering = ['name']

    def __str__(self):
        return self.name
