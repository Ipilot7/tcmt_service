
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Администратор'
        MANAGER = 'manager', 'Менеджер'
        USER = 'user', 'Пользователь'

    full_name = models.CharField(max_length=255)
    passport = models.CharField(max_length=20)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER
    )

    def __str__(self):
        return self.full_name
