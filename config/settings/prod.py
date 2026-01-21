from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    "192.168.0.79",
    "service.deepfocus.uz",
    "localhost",
    "127.0.0.1"
]

# Security Settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
APPEND_SLASH = True

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    "https://service.deepfocus.uz",  # Update with your actual domain
]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
