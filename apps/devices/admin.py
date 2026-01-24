from django.contrib import admin
from .models import DeviceType, Device

@admin.register(DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'device_type', 'hospital')
    list_filter = ('device_type', 'hospital')
    search_fields = ('serial_number',)
