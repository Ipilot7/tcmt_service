from django.db import models

class StatusChoices(models.TextChoices):
    NEW = 'NW', 'New'
    PENDING = 'PD', 'Pending'
    COMPLETED = 'CP', 'Completed'
    CANCELED = 'CN', 'Canceled'
    ON_HOLD = 'OH', 'On Hold'
