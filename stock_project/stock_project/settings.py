"""
Django settings for stock_project project.
"""
import os
from pathlib import Path
from decouple import config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================
# Security & Debug Configuration (.env)
# ==========================================
SECRET_KEY = config('SECRET_KEY', default='django-insecure-fzgbdzn!wtcrkt3vtwi9j*@-=y_qece!zdolfr5&te**n5h2ct')
DEBUG = config('DEBUG', default=True, cast=bool)

# กำหนด ALLOWED_HOSTS รองรับทั้ง Localhost และ Host จริง
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost,*', cast=Csv())

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Custom Apps
    'parts_app',
    'accounts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # จัดการ Static Files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'stock_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'stock_project.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'th'
TIME_ZONE = 'Asia/Bangkok'
USE_I18N = True
USE_TZ = True

# ==========================================
# Static & Media Files Configuration
# ==========================================
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'parts_app' / 'static',
]

# ใช้ WhiteNoise ให้ดึงและบีบอัดไฟล์โดยตรง ไม่พังแม้หาบางไฟล์ไม่เจอ
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_USE_FINDERS = True

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==========================================
# Email Configuration (.env)
# ==========================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-relay.brevo.com'
EMAIL_PORT = 2525
EMAIL_USE_SSL = False
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 30
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')

# ==========================================
# Logging Configuration
# ==========================================
# ค่า default ของ Django จะพิมพ์ error ออก console ก็ต่อเมื่อ DEBUG=True เท่านั้น
# ทำให้ตอน production (DEBUG=False บน Render) exception ที่เกิดขึ้นจริง (เช่นตอน
# send_mail ผิดพลาด) ไม่โผล่ใน Render Logs เลย เห็นแค่ "500" เฉย ๆ หา sebab ไม่ได้
# ตั้งค่านี้เพิ่มเพื่อบังคับให้พิมพ์ traceback ออก console เสมอ ไม่ว่า DEBUG จะเป็นอะไร
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# ==========================================
# Default Primary Key
# ==========================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'