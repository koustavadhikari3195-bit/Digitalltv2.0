"""
DIGITALLY — Production Settings
PostgreSQL (Supabase), Redis cache, HTTPS enforcement.
"""
import dj_database_url
from .base import *  # noqa: F401, F403
import os

DEBUG = False
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["digitally-v2.vercel.app", ".vercel.app"])

# Database — Supabase PostgreSQL
DATABASE_URL = env("DATABASE_URL", default=None)

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
            engine="django.db.backends.postgresql",
        )
    }
    DATABASES["default"]["OPTIONS"] = {"options": "-c search_path=public"}
    # Disable server-side cursors for request-pooling (Supabase/PgBouncer)
    DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = True
else:
    # Fallback to SQLite for build-time or if DB_URL is missing
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
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

# Static files - Whitenoise
if "whitenoise.middleware.WhiteNoiseMiddleware" not in MIDDLEWARE:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media Files — Supabase Storage (S3)
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="media")
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL")
AWS_S3_REGION_NAME = "us-east-1"  # Supabase uses this region for compatibility
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None

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
