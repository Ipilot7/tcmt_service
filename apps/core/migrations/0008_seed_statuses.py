from django.db import migrations

def seed_statuses(apps, schema_editor):
    Status = apps.get_model('core', 'Status')
    statuses = [
        ('initial', 'Initial'),
        ('in_progress', 'In Progress'),
        ('success', 'Success'),
        ('canceled', 'Canceled'),
    ]
    for name, display in statuses:
        Status.objects.get_or_create(name=name)

def reverse_statuses(apps, schema_editor):
    Status = apps.get_model('core', 'Status')
    Status.objects.filter(name__in=['initial', 'in_progress', 'success', 'canceled']).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_equipment_equipment_type'),
    ]

    operations = [
        migrations.RunPython(seed_statuses, reverse_statuses),
    ]
