import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.accounts.models import User
from apps.core.notifications import send_push_notification

user = User.objects.filter(telegram_id='1611823189').first()
if user:
    print(f"Sending test notification to {user.fullname}...")
    res = send_push_notification(
        user=user,
        title="Тестовое уведомление",
        body="Это проверка системы уведомлений."
    )
    print(f"Result: {res}")
else:
    print("User with telegram_id 1611823189 not found.")
