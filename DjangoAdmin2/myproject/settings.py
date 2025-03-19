import os
from pathlib import Path
from datetime import timedelta

# 建立 BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# 添加 SECRET_KEY 設置
SECRET_KEY = 'your-secret-key-here'  # 請替換為一個長的、隨機的字符串

# 添加 DEBUG 設置
DEBUG = True  # 在開發環境中設置為 True，生產環境中應該設置為 False

# 添加 ALLOWED_HOSTS 設置
ALLOWED_HOSTS = ['localhost', '127.0.0.1']  # 添加您的域名或 IP 地址

# 其他應用...

INSTALLED_APPS = [
    'myapp',  # 确保这行在 django.contrib.auth 之前
    'restaurant_system',
    'shopping_system',
    'trip_planner',
    'theme_entertainment.apps.ThemeEntertainmentConfig',  # 確保這行存在
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',  # 添加這行
    'forum_system',  # 新增的應用
    'travel_app',
    'rest_framework',
    'django_filters',
    'corsheaders',
    'django_ckeditor_5',  # 使用新的 CKEditor 5
    'rest_framework_simplejwt',
    'django_celery_results',
    'password_reset',  # 新增的密碼重設應用
]


# 添加 MIDDLEWARE 設置
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # 這行須在最前面
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS 設置
CORS_ALLOW_ALL_ORIGINS = True  # 允許所有來源的跨域請求
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
CORS_EXPOSE_HEADERS = [
    'content-disposition',
]
CORS_PREFLIGHT_MAX_AGE = 86400  # 預檢請求的有效期，單位秒
CORS_ALLOW_CREDENTIALS = True  # 允許跨域請求攜帶憑證（如Cookie）

# 添加 ROOT_URLCONF 設置
ROOT_URLCONF = 'myproject.urls'

# 添加 TEMPLATES 設置
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'myapp', 'templates'),
            os.path.join(BASE_DIR, 'theme_entertainment', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'myapp.context_processors.message_count',
            ],
        },
    },
]

# 數據庫設置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'fun'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'P@ssw0rd'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES';",
            'charset': 'utf8mb4',
        },
    }
}

# 添加這行來指定自定義用戶模型
AUTH_USER_MODEL = 'myapp.Member'

# 登入相關設置
LOGIN_URL = '/login/'  # 確保這個路徑與您的登入URL匹配
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'

# 其他應用...

# 在文件的頂部附近添加這行
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 添加語言和時區設置
LANGUAGE_CODE = 'zh-hant'
TIME_ZONE = 'Asia/Taipei'
USE_I18N = True
USE_L10N = True
USE_TZ = False

# 修改靜態文件設置
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# 媒體文件設置
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 在文件的底部添加以下內容

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'myapp': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['file'],
            'level': 'INFO',  # 將級別從 DEBUG 改為 INFO，以關閉詳細的數據庫查詢日誌
            'propagate': False,
        },
    },
}

X_FRAME_OPTIONS = 'SAMEORIGIN'

# 更新 CKEditor 5 配置
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|',
            'bold', 'italic', 'underline', 'strikethrough', '|',
            'bulletedList', 'numberedList', '|',
            'blockQuote', 'imageUpload', '|',
            'link', 'unlink', '|',
            'undo', 'redo', '|',
            'alignment', 'indent', 'outdent', '|',
            'horizontalLine', 'insertTable', '|',
            'fontBackgroundColor', 'fontColor', 'fontSize', 'fontFamily', '|',
            'removeFormat', 'sourceEditing'
        ],
        'height': '400px',
        'width': '100%',
        'language': 'zh',
        'image': {
            'toolbar': [
                'imageTextAlternative', '|',
                'imageStyle:alignLeft', 'imageStyle:alignCenter', 'imageStyle:alignRight', '|',
                'resizeImage'
            ],
            'styles': [
                'alignLeft', 'alignCenter', 'alignRight'
            ],
            'resizeUnit': 'px'
        },
    }
}

# REST Framework 設置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# JWT 設置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(days=1),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
}

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Taipei'

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Google OAuth2 設定
GOOGLE_CLIENT_ID = '1063055916047-ic94ldh4ojm4gg18sbcqmenerdc98s2s.apps.googleusercontent.com'

# 添加郵件設定
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'lf2net67983@gmail.com'
EMAIL_HOST_PASSWORD = 'yoaq xubu djsw eabf'  # 更新的 Gmail 應用程式密碼
DEFAULT_FROM_EMAIL = 'Travel Fun <lf2net67983@gmail.com>'

# 密碼重設 Token 有效期 (1 小時)
PASSWORD_RESET_TIMEOUT = 3600
