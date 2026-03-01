import os
import requests
import firebase_admin
from firebase_admin import credentials, messaging
import logging
from django.conf import settings
from django.db.models import Q

logger = logging.getLogger(__name__)

def initialize_firebase():
    """
    Initializes the Firebase Admin SDK.
    Requires FIREBASE_SERVICE_ACCOUNT_PATH in settings (from .env).
    """
    if not firebase_admin._apps:
        service_account_path = getattr(settings, 'FIREBASE_SERVICE_ACCOUNT_PATH', None)
        if service_account_path and os.path.exists(service_account_path):
            try:
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
            except Exception as e:
                logger.error(f"Error initializing Firebase: {e}")
        else:
            logger.warning("FIREBASE_SERVICE_ACCOUNT_PATH not found or file does not exist. Push notifications will be disabled.")

def send_telegram_notification(user, text):
    """
    Sends a message via Telegram bot if the user has a telegram_id.
    """
    if not user.telegram_id:
        logger.warning(f"Skipping Telegram notification for user {user.id}: no telegram_id")
        return None
    
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error(f"Skipping Telegram notification: TELEGRAM_BOT_TOKEN not set in settings")
        return None
    
    logger.info(f"Attempting to send Telegram notification to user {user.id} (TG: {user.telegram_id})")
    
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": user.telegram_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        logger.info(f"Telegram notification sent to user {user.id}")
        return response.json()
    except Exception as e:
        logger.error(f"Error sending Telegram notification to user {user.id}: {e}")
        if hasattr(e, 'response') and e.response is not None:
             logger.error(f"Telegram API response: {e.response.text}")
        return None

def send_push_notification(user, title, body, data=None):
    """
    Sends a push notification to all FCM tokens AND Telegram.
    """
    # Send Telegram notification as well
    telegram_text = f"🔔 <b>{title}</b>\n\n{body}"
    send_telegram_notification(user, telegram_text)

    initialize_firebase()
    
    if not firebase_admin._apps:
        return []

    tokens = user.fcm_tokens.values_list('token', flat=True)
    if not tokens:
        return []

    message_bodies = []
    for token in tokens:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            token=token,
        )
        message_bodies.append(message)

    if not message_bodies:
        return []

    try:
        # Batch sending (up to 500 messages at once)
        response = messaging.send_all(message_bodies)
        logger.info(f"Successfully sent {response.success_count} notifications for user {user.id}")
        return response
    except Exception as e:
        logger.error(f"Error sending notifications to user {user.id}: {e}")
        return None

def notify_managers(title, body, data=None):
    """
    Sends notifications to all users with 'Manager' role or staff status.
    """
    from apps.accounts.models import User
    
    # Use the same logic as IsAdminOrManager permission
    managers = User.objects.filter(
        Q(is_superuser=True) | 
        Q(is_staff=True) | 
        Q(roles__name__iexact='Manager')
    ).distinct()

    for manager in managers:
        send_push_notification(manager, title, body, data)
