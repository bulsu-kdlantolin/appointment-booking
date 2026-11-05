"""
Django settings for config project.
"""

from pathlib import Path
from django.urls import reverse_lazy
from django.templatetags.static import static

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-_!d_dni4$yeq265&apu#2#6@l+b*44v)-1u7nlx&uz2251o(!7'

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'testserver', '*']

INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'appointments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'appointments.middleware.Custom404Middleware',
]

X_FRAME_OPTIONS = 'SAMEORIGIN'


ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'appointments' / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
LOGIN_REDIRECT_URL = '/admin/'


UNFOLD = {
    "SITE_TITLE": "Appointment Booking Admin",
    "SITE_HEADER": "Appointment Booking",
    "SITE_SUBHEADER": "Administration Dashboard",
    "SITE_URL": "/",
    "SITE_ICON": lambda request: static("images/logo.svg"),
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "any",
            "type": "image/svg+xml",
            "href": lambda request: static("images/logo.svg"),
        }
    ],
    "COLORS": {
        "primary": {
            "50": "239 246 255",
            "100": "219 234 254",
            "200": "191 219 254",
            "300": "147 197 253",
            "400": "96 165 250",
            "500": "59 130 246",
            "600": "37 99 235",
            "700": "29 78 216",
            "800": "30 64 175",
            "900": "30 58 138",
            "950": "23 37 84",
        },
    },
    "STYLES": [
        lambda request: static("css/admin_fonts.css"),
        lambda request: static("vendor/flatpickr/flatpickr.min.css"),
        lambda request: static("css/flatpickr_theme.css"),
        lambda request: static("css/custom_dropdown.css"),
        lambda request: static("css/auto_dismiss_errors.css"),
        lambda request: static("css/admin_permissions.css"),
    ],
    "SCRIPTS": [
        lambda request: static("js/admin_theme_default.js"),
        lambda request: static("vendor/flatpickr/flatpickr.min.js"),
        lambda request: static("js/custom_dropdown.js"),
        lambda request: static("js/admin_datetime_picker.js"),
        lambda request: static("js/flatpickr_ampm_toggle.js"),
        lambda request: static("js/auto_dismiss_errors.js"),
        lambda request: static("js/admin_permissions.js"),
    ],
    "SIDEBAR": {
        "show_search": False,
        "show_all_applications": False,
        "navigation": [
            {
                "items": [
                    {
                        "title": "Appointment",
                        "icon": "calendar_month",
                        "link": reverse_lazy("admin:app_list", args=["appointments"]),
                        "items": [
                            {
                                "title": "Appointments",
                                "icon": "event_available",
                                "link": reverse_lazy("admin:appointments_appointment_changelist"),
                            },
                            {
                                "title": "Clients",
                                "icon": "person",
                                "link": reverse_lazy("admin:appointments_client_changelist"),
                            },
                            {
                                "title": "Services",
                                "icon": "medical_services",
                                "link": reverse_lazy("admin:appointments_service_changelist"),
                            },
                        ],
                    },
                    {
                        "title": "Authentication",
                        "icon": "admin_panel_settings",
                        "link": reverse_lazy("admin:app_list", args=["auth"]),
                        "items": [
                            {
                                "title": "Users",
                                "icon": "account_circle",
                                "link": reverse_lazy("admin:auth_user_changelist"),
                            },
                            {
                                "title": "Groups",
                                "icon": "groups",
                                "link": reverse_lazy("admin:auth_group_changelist"),
                            },
                        ],
                    },
                ],
            },
        ],
    },
}
