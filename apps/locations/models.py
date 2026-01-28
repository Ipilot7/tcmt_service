from django.db import models

class Region(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'regions'
        verbose_name = 'Region'
        verbose_name_plural = 'Regions'
        ordering = ['name']

    def __str__(self):
        return self.name

class Hospital(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    lat = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    long = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name='hospitals')

    class Meta:
        db_table = 'hospitals'
        verbose_name = 'Hospital'
        verbose_name_plural = 'Hospitals'
        ordering = ['name']

    def __str__(self):
        return self.name

class HospitalMaintenance(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='maintenances')
    maintenance_date = models.DateField()

    class Meta:
        db_table = 'hospital_maintenance'
        unique_together = ('hospital', 'maintenance_date')
        verbose_name = 'Hospital Maintenance'
        verbose_name_plural = 'Hospital Maintenances'
        ordering = ['-maintenance_date']

    def __str__(self):
        return f"{self.hospital.name} - {self.maintenance_date}"
