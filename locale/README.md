This directory contains translation files.
python manage.py makemessages -l ru -l en -l uz
Open the generated .po files in the locale/ directory (e.g., locale/en/LC_MESSAGES/django.po) and fill in the English translations for the Russian strings.
python manage.py compilemessages