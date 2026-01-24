from django.contrib import admin
from .models import User, Role, Permission

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'psn')
    search_fields = ('fullname', 'psn')

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('users',)

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('roles',)
