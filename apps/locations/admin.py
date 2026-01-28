from django.contrib import admin
from .models import Region, Hospital, HospitalMaintenance

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'lat', 'long')
    list_filter = ('region',)
    search_fields = ('name',)

@admin.register(HospitalMaintenance)
class HospitalMaintenanceAdmin(admin.ModelAdmin):
    list_display = ('hospital', 'maintenance_date')
    list_filter = ('hospital', 'maintenance_date')
