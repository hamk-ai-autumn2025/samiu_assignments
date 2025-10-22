from pathlib import Path

# --- Perusasetukset ---
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "dev-secret-key-change-if-deploying"
DEBUG = True
ALLOWED_HOSTS = ["*"]  # paikalliselle kehitykselle ok

# --- Sovellukset ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "farm",  # ← sinun appisi
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mysite.urls"

# --- Templatet ---
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # projektin yleiset templatet
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "mysite.wsgi.application"

# --- Tietokanta ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# --- Kieli ja aikavyöhyke ---
LANGUAGE_CODE = "fi-fi"
TIME_ZONE = "Europe/Helsinki"
USE_I18N = True
USE_TZ = True

# --- Static ---
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]  # vapaaehtoinen, jos käytät projektin static-kansiota

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
