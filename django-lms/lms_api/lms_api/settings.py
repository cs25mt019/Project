"""
Django settings for lms_api project.
"""

import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-xm%7=t_j(acs5y(ee&j5%1)bg8ag@498@a=%nf!(s))vyg$2j&'
DEBUG = True

ALLOWED_HOSTS = ["*"]

# ==========================================
# INSTALLED APPS
# ==========================================

INSTALLED_APPS = [
    "main",
    "rest_framework",
    "rest_framework.authtoken",
   # "rest_framework_simplejwt.token_blacklist",
    "corsheaders",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# ==========================================
# MIDDLEWARE  (ORDER MATTERS!)
# ==========================================

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",

    # IMPORTANT: Disable CSRF for API-only JWT usage
    # You can comment this out safely
    # "django.middleware.csrf.CsrfViewMiddleware",

    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "lms_api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "lms_api.wsgi.application"

# ==========================================
# DATABASE
# ==========================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "django_lms"),
        "USER": os.getenv("DB_USER", "root"),
        "PASSWORD": os.getenv("DB_PASSWORD", "Case@27032002"),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3306"),
    }
}

# ==========================================
# PASSWORD VALIDATORS
# ==========================================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ==========================================
# REST FRAMEWORK CONFIG
# ==========================================

# In settings.py, update REST_FRAMEWORK settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "main.custom_auth.CustomJWTAuthentication",  # Use custom auth
        # "rest_framework_simplejwt.authentication.JWTAuthentication",  # Remove this
    ),
    "UNAUTHENTICATED_USER": None,
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
}
# ==========================================
# SIMPLE JWT CONFIG
# ==========================================

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ==========================================
# INTERNATIONALIZATION
# ==========================================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ==========================================
# STATIC & MEDIA
# ==========================================

STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# ==========================================
# CORS
# ==========================================

CORS_ALLOW_ALL_ORIGINS = True
X_FRAME_OPTIONS = "ALLOWALL"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp-relay.brevo.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# THIS MUST MATCH BREVO LOGIN USERNAME (NOT YOUR GMAIL!)
EMAIL_HOST_USER = "9bb1f8001@smtp-brevo.com"

# THIS IS YOUR SMTP KEY (not API key, not Gmail password)
EMAIL_HOST_PASSWORD = "xsmtpsib-7352969d369eb88b539c2fd1a2e57bd918658fd40045693f07307af3b81ad5bb-dxuZs1WRCuKe6pH3"

# This is what recipient sees
DEFAULT_FROM_EMAIL = "sahilrocky930@gmail.com"
