from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
ALLOWED_HOSTS = ['http://10.200.20.123',"localhost", "127.0.0.1"]

# Добавьте это в настройки
CSRF_TRUSTED_ORIGINS = [
    'https://service.deepfocus.uz',
    'http://service.deepfocus.uz',
    'http://10.200.20.123',
]
# Это говорит Django доверять заголовку от Cloudflare/Nginx о том, что был HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True