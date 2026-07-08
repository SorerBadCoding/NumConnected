"""
Production settings.

Secrets and host configuration are pulled from environment variables so the
same codebase can be deployed without editing source. Set at minimum:

    DJANGO_SECRET_KEY
    DJANGO_ALLOWED_HOSTS   (comma separated)
    DATABASE_URL           (provided automatically by Railway's Postgres plugin)

SQLite is used only if DATABASE_URL is unset — fine for a quick trial, but
switch to a managed Postgres before storing real data, since most platform
filesystems (including Railway's) are ephemeral.
"""

import os

import dj_database_url

from .base import *  # noqa: F401,F403

DEBUG = False

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", SECRET_KEY)

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]

# Railway injects this for services with a public domain — picked up
# automatically so a fresh deploy works before DJANGO_ALLOWED_HOSTS is set.
_railway_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
if _railway_domain and _railway_domain not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_railway_domain)

# ---------------------------------------------------------------------------
# Database — Postgres via DATABASE_URL (Railway, Render, Heroku, etc.)
# ---------------------------------------------------------------------------

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

# ---------------------------------------------------------------------------
# Static files — WhiteNoise serves them directly from the app process, no
# separate nginx/CDN needed for a project this size.
# ---------------------------------------------------------------------------

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# ---------------------------------------------------------------------------
# Security hardening
# ---------------------------------------------------------------------------

# Railway (like Heroku/Render) terminates TLS at the edge and forwards plain
# HTTP internally with this header — without it, SECURE_SSL_REDIRECT causes
# an infinite redirect loop because Django never sees the request as secure.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

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
if _railway_domain and f"https://{_railway_domain}" not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append(f"https://{_railway_domain}")

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
