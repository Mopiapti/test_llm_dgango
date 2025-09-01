from pathlib import Path
import os
from dotenv import load_dotenv
from chatapi.services import llm_prompt_example as prompt

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-++rcm&eem!e4^f99!$gco0i&(@y5ojm#3*o69$08#+3j1-z1m4'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    "rest_framework", 
    "corsheaders",
    "constance",
    "drf_spectacular",

    "products", 
    "chatapi"
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'


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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication"
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated"
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# Redis Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MOCK_MODE = os.getenv('OPENAI_MOCK_MODE', 'True').lower() == 'true'

# CONSTANCE
CONSTANCE_CONFIG = {
    "LLM_PROVIDER": (
        "anthropic",
        "LLM Provider name",
        str,
    ),
    "LLM_MODEL": (
        "claude-3-5-sonnet-latest",
        "LLM Model name",
        str,
    ),
    "LLM_TEMPERATURE_FOR_SQL": (
        0.1,
        "LLM Temperature",
        float,
    ),
    "LLM_SYSTEM_PROMPT_FOR_SQL": (
        prompt.LLM_SYSTEM_PROMPT_FOR_SQL,
        "LLM System prompt",
        str,
    ),   
    "LLM_TEMPERATURE_FOR_REPLY": (
        0.5,
        "LLM Temperature",
        float,
    ),
    "LLM_SYSTEM_PROMPT_FOR_REPLY": (
        prompt.LLM_SYSTEM_PROMPT_FOR_REPLY,
        "LLM System prompt",
        str,
    ),
    "LLM_SYSTEM_PROMPT_WITH_TOOLS": (
        prompt.LLM_SYSTEM_PROMPT_WITH_TOOLS,
        "LLM System prompt",
        str,
    ),
    "LLM_SYSTEM_PROMPT_WITH_TOOLS_AND_FILTERS": (
        prompt.LLM_SYSTEM_PROMPT_WITH_TOOLS_AND_FILTERS,
        "LLM System prompt",
        str,
    ),
    "TOP_K": (
        10,
        "Top K results to return from database",
        int,
    )
}

CONSTANCE_IGNORE_ADMIN_VERSION_CHECK = True
CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
#CONSTANCE_DATABASE_CACHE_BACKEND = 'default'
#CONSTANCE_BACKEND = 'constance.backends.redisd.RedisBackend'

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')


# Spectacular settings for Swagger
SPECTACULAR_SETTINGS = {
    'TITLE': 'Chat API',
    'DESCRIPTION': 'API for LLM Chat System with SQL Query Generation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    
    # Authentication
    'COMPONENT_SPLIT_REQUEST': True,
    'COMPONENT_NO_READ_ONLY_REQUIRED': True,
    
    # UI Settings
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'filter': True,
    },
    
    # Security schemes
    'AUTHENTICATION_WHITELIST': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}