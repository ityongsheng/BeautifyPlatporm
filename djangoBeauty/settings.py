from pathlib import Path

# 构建基本路径
BASE_DIR = Path(__file__).resolve().parent.parent

# 安全密钥（开发环境随意，生产环境需保密）
SECRET_KEY = 'django-insecure-test-key-for-beauty-shop-project'

# 调试模式（开发开启）
DEBUG = True

ALLOWED_HOSTS = ['*']

# 应用注册（核心部分）
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 第三方库
    'rest_framework',
    'corsheaders',
    'django_filters',  # 如果刚才装了这个

    # --- 必须加上这一行！---
    'app',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # 跨域中间件
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'djangoBeauty.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'djangoBeauty.wsgi.application'

# 数据库配置
# 为了让你能立即运行，这里先配置为 SQLite。
# 如果需要 MySQL，请将下方注释解开并配置你的 MySQL 账号密码。
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 密码验证
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
]

# 国际化配置（设置为中文）
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# 静态文件
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 指定我们自定义的用户模型
AUTH_USER_MODEL = 'app.UserProfile'

# 跨域配置（允许前端访问）
CORS_ALLOW_ALL_ORIGINS = True