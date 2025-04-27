"""
WSGI config for myday project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

# Use settings_prod for Render deployment
if os.environ.get('RENDER', '').lower() == 'true':
    print("Running on Render, using settings_prod.py", file=sys.stderr)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myday.settings_prod')
else:
    print("Running locally, using settings.py", file=sys.stderr)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myday.settings')

application = get_wsgi_application()
