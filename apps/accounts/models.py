from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, login, password=None, **extra_fields):
        if not login:
            raise ValueError('Логин обязателен')
        user = self.model(login=login, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(login, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    fullname = models.CharField(max_length=255, db_index=True)
    psn = models.CharField(max_length=255)
    login = models.CharField(max_length=255, unique=True)
    
    # Служебные поля для работы админки
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    # Исправление конфликта имен
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups', # Уникальное имя для обратной связи
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions', # Уникальное имя для обратной связи
        blank=True,
    )

    objects = UserManager()

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['fullname']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['fullname']

    def __str__(self):
        return self.fullname

class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)
    # Используем строку 'User', так как класс определен выше
    users = models.ManyToManyField('User', related_name='roles', db_table='user_roles', blank=True)

    class Meta:
        db_table = 'roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['name']

    def __str__(self):
        return self.name

class Permission(models.Model):
    name = models.CharField(max_length=255, unique=True)
    roles = models.ManyToManyField(Role, related_name='permissions', db_table='role_permissions', blank=True)

    class Meta:
        db_table = 'permissions'
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'
        ordering = ['name']

    def __str__(self):
        return self.name