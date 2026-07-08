"""
Production settings.

Secrets and host configuration are pulled from environment variables so the
same codebase can be deployed without editing source. Set at minimum:

    DJANGO_SECRET_KEY
    DJANGO_ALLOWED_HOSTS   (comma separated)

Swap the SQLite DATABASES entry for a managed database (Postgres, etc.)
before going live — SQLite is intended for development only.
"""

import os

from .base import *  # noqa: F401,F403

DEBUG = False

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", SECRET_KEY)

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]

# ---------------------------------------------------------------------------
# Security hardening
# ---------------------------------------------------------------------------

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 7
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

AI_ASSISTANT_PROVIDER = os.environ.get("AI_ASSISTANT_PROVIDER", "local")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}
