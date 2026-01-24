from django.db import models

class User(models.Model):
    fullname = models.CharField(max_length=255, db_index=True)
    psn = models.CharField(max_length=255)  # SQL has CHAR(255), CharField is fine

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['fullname']

    def __str__(self):
        return self.fullname

class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)
    users = models.ManyToManyField(User, related_name='roles', db_table='user_roles')

    class Meta:
        db_table = 'roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['name']

    def __str__(self):
        return self.name

class Permission(models.Model):
    name = models.CharField(max_length=255, unique=True)
    roles = models.ManyToManyField(Role, related_name='permissions', db_table='role_permissions')

    class Meta:
        db_table = 'permissions'
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'
        ordering = ['name']

    def __str__(self):
        return self.name
