from pathlib import Path
from datetime import timedelta # Asegúrate que esta línea esté presente

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-d1y7=5zm2pmwg!$wrlcsd+qwh$yk!4h6$#qavof#n1re+bnr#o' # Manten tu SECRET_KEY original

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# MODIFICADO/AÑADIDO: Configura los hosts permitidos
ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts', # Tu app
    'rest_framework', # Django REST framework
    'rest_framework_simplejwt', # Simple JWT
]

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware', # Esta línea es la que hace la comprobación CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.AuthRequiredMiddleware', # Asumo que este es un middleware tuyo personalizado
]

ROOT_URLCONF = 'finanzia.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'finanzia.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us' # Puedes cambiarlo a 'es' si tu app es en español

TIME_ZONE = 'UTC' # Puedes cambiarlo a tu zona horaria, ej: 'America/Bogota'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# AÑADIDO: Para permitir solicitudes POST desde estos orígenes cuando se usa HTTPS
CSRF_TRUSTED_ORIGINS = [
    'https://localhost:8000',
    'https://127.0.0.1:8000',
]

# Configuración para Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
    # Si quieres que TODAS las vistas de API requieran autenticación por defecto,
    # puedes añadir también (esto es opcional por ahora y puedes decidirlo después):
    # 'DEFAULT_PERMISSION_CLASSES': (
    #     'rest_framework.permissions.IsAuthenticated',
    # )
}

# Configuración para Simple JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),  # Tiempo de vida del token de acceso (ej: 30 minutos)
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),    # Tiempo de vida del token de refresco (ej: 1 día)
    "ROTATE_REFRESH_TOKENS": False, # False es más simple para empezar
    "BLACKLIST_AFTER_ROTATION": False, # False es más simple para empezar

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY, # Usa la SECRET_KEY de Django. ¡Muy importante que sea segura en producción!
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",), # "Bearer" es el prefijo estándar para enviar el token
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION", # Nombre del encabezado HTTP
    "USER_ID_FIELD": "id", # Campo del modelo de usuario que se usará como identificador
    "USER_ID_CLAIM": "user_id", # Nombre del claim en el JWT para el ID de usuario
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type", # Claim para el tipo de token
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser", # Clase para el usuario del token

    "JTI_CLAIM": "jti", # Claim para el ID único del JWT
}