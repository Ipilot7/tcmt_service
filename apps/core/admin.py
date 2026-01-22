from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Region, Institution, EquipmentType, Status, Equipment

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'sale_date', 'get_warranty_end', 'get_is_under_warranty')
    list_filter = ('region',)
    search_fields = ('name',)
    filter_horizontal = ('equipments',)

    def get_warranty_end(self, obj):
        return obj.warranty_end
    get_warranty_end.short_description = _('Warranty End')

    def get_is_under_warranty(self, obj):
        return obj.is_under_warranty
    get_is_under_warranty.boolean = True
    get_is_under_warranty.short_description = _('Under Warranty')

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('equipment_type', 'serial_number', 'get_institution', 'get_warranty_status')
    list_filter = ('equipment_type',)
    search_fields = ('serial_number',)

    def get_institution(self, obj):
        # Taking the first related institution (if any)
        inst = obj.institutions.first()
        return inst.name if inst else "---"
    get_institution.short_description = _('Institution')

    def get_warranty_status(self, obj):
        inst = obj.institutions.first()
        if inst:
            return inst.is_under_warranty
        return None
    get_warranty_status.boolean = True
    get_warranty_status.short_description = _('Under Warranty')

admin.site.register(Region)
admin.site.register(EquipmentType)
admin.site.register(Status)
