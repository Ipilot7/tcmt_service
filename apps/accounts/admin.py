from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role, Permission, FCMToken
from apps.core.notifications import send_push_notification
from .forms import UserCreationForm, UserChangeForm

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Убираем фильтры и поля, которых нет в нашей модели (например, date_joined)
    list_display = ('login', 'fullname', 'psn', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('login', 'fullname', 'psn')
    ordering = ('fullname',)
    actions = ['send_custom_notification']

    @admin.action(description="Отправить тестовое уведомление")
    def send_custom_notification(self, request, queryset):
        sent_count = 0
        for user in queryset:
            send_push_notification(
                user=user,
                title="Тестовое уведомление",
                body="Это тестовое уведомление от администратора.",
                data={"type": "admin_test"}
            )
            sent_count += 1
        self.message_user(request, f"Отправлено {sent_count} уведомлений.", messages.SUCCESS)

    form = UserChangeForm
    add_form = UserCreationForm

    fieldsets = (
        (None, {'fields': ('login', 'password')}),
        ('Личные данные', {'fields': ('fullname', 'psn')}),
        ('Права', {'fields': ('is_active', 'is_staff', 'is_superuser', 'roles', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('login', 'fullname', 'psn', 'password1', 'password2', 'roles'),
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

@admin.register(FCMToken)
class FCMTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at')
    search_fields = ('user__fullname', 'token')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)