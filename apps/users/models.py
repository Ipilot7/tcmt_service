
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', _('Administrator')
        MANAGER = 'manager', _('Manager')
        USER = 'user', _('User')

    full_name = models.CharField(_('Full Name'), max_length=255)
    passport = models.CharField(_('Passport'), max_length=20)
    role = models.CharField(
        _('Role'),
        max_length=20,
        choices=Role.choices,
        default=Role.USER
    )

    def __str__(self):
        return self.full_name
