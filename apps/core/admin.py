from django.contrib import admin
from .models import Region, Institution, EquipmentType, Status

admin.site.register(Region)
admin.site.register(Institution)
admin.site.register(EquipmentType)
admin.site.register(Status)
