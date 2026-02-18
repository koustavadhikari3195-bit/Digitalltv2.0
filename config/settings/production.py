"""
DIGITALLY — Production Settings
PostgreSQL (Supabase), Redis cache, HTTPS enforcement.
"""
import dj_database_url
from .base import *  # noqa: F401, F403

DEBUG = False
ALLOWED_HOSTS = env("ALLOWED_HOSTS")  # noqa: F405

# Database — Supabase PostgreSQL
DATABASES = {
    "default": dj_database_url.config(
        default=env("DATABASE_URL", default=""),  # noqa: F405
        conn_max_age=600,
        ssl_require=True,
    )
}

# Cache — Redis for production
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "digitally-prod-cache",
        # Switch to Redis when available:
        # "BACKEND": "django_redis.cache.RedisCache",
        # "LOCATION": env("REDIS_URL", default="redis://127.0.0.1:6379/1"),
    }
}

# Security
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# CSP — strict for production
CSP_DEFAULT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_IMG_SRC = ("'self'", "data:")
CSP_FONT_SRC = ("'self'",)
CSP_CONNECT_SRC = ("'self'",)
