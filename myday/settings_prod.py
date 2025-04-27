"""
Production settings for myday project.
"""

import os
import sys
import dj_database_url
from .settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'

# Allow all host headers
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*.onrender.com,.onrender.com,myday-gla-dsuw.onrender.com,localhost,127.0.0.1').split(',')

# Add CSRF trusted origins for Render
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://myday-gla-dsuw.onrender.com',
]

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    'https://myday.onrender.com',
    'https://myday-gla-dsuw.onrender.com',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Override secret key in production
if 'DJANGO_SECRET_KEY' in os.environ:
    SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# Update middleware for production
# Add cache middleware at the beginning
MIDDLEWARE.insert(0, 'django.middleware.cache.UpdateCacheMiddleware')

# Add whitenoise for static files (after UpdateCacheMiddleware)
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Add compression middleware for faster page loads
MIDDLEWARE.insert(2, 'django.middleware.gzip.GZipMiddleware')

# Add Render wakeup middleware for handling sleep mode
MIDDLEWARE.insert(3, 'myday.render_middleware.RenderWakeupMiddleware')

# Add FetchFromCacheMiddleware at the end
MIDDLEWARE.append('django.middleware.cache.FetchFromCacheMiddleware')

# Static files configuration
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Use a simpler storage that doesn't require a manifest
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Configure database using DATABASE_URL environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Parse the DATABASE_URL
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,  # Keep connections open for 10 minutes
            conn_health_checks=True,  # Check connection health before using
            ssl_require=False,  # Set to False for Render internal connections
        )
    }

    # Add connection pooling options for better performance
    DATABASES['default']['OPTIONS'] = {
        'connect_timeout': 30,  # 30 seconds connection timeout
        'keepalives': 1,  # Enable keepalives
        'keepalives_idle': 60,  # Seconds between keepalives
        'keepalives_interval': 10,  # Seconds between keepalive probes
        'keepalives_count': 5,  # Number of keepalive probes
    }

    # Print database configuration for debugging
    print(f"Using PostgreSQL database from DATABASE_URL", file=sys.stderr)
    print(f"Database engine: {DATABASES['default']['ENGINE']}", file=sys.stderr)
    print(f"Database name: {DATABASES['default']['NAME']}", file=sys.stderr)
    print(f"Database host: {DATABASES['default']['HOST']}", file=sys.stderr)
    print(f"Connection pool settings: conn_max_age={DATABASES['default']['CONN_MAX_AGE']}", file=sys.stderr)
else:
    print("No DATABASE_URL found, using SQLite as fallback", file=sys.stderr)

# Security settings
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Cache settings for better performance
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 minutes
    }
}

# Cache middleware settings
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 600  # 10 minutes
CACHE_MIDDLEWARE_KEY_PREFIX = 'myday'

# Enable HTTPS settings for Render
# Temporarily disable SSL redirect for debugging
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0  # Disabled for now
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# File Storage settings
# Using Cloudinary for media storage
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', 'dbxwr2avj'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', '353298813117544'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', '0-tBjIKSrVMiYFaN9AxNleOV-eg')
}

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'sanataniaryan010@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'uodh xzmk jbns abag')

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'render_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'myday': {
            'handlers': ['render_console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
