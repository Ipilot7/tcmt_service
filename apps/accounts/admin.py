from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role, Permission

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Убираем фильтры и поля, которых нет в нашей модели (например, date_joined)
    list_display = ('login', 'fullname', 'psn', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('login', 'fullname', 'psn')
    ordering = ('fullname',)

    fieldsets = (
        (None, {'fields': ('login', 'password')}),
        ('Личные данные', {'fields': ('fullname', 'psn')}),
        ('Права', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    # Это решит проблему "Add User"
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('login', 'fullname', 'psn', 'password'),
        }),
    )

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('users',) # Удобный интерфейс выбора пользователей

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('roles',) # Удобный интерфейс выбора ролей