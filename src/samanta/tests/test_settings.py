SECRET_KEY = 'fake-key'
# Custom user model
AUTH_USER_MODEL = 'samanta.SamUser'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'captcha',
    'samanta'
]