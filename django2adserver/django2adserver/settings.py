"""
Django settings for django2adserver project.

Generated by 'django-admin startproject' using Django 2.1.10.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#MEDIA_ROOT =os.path.join(BASE_DIR,'delivery/media/')
MEDIA_ROOT =os.path.join(BASE_DIR,'../public_html/pydelivery/media/')
#MEDIA_ROOT =os.path.join(BASE_DIR,'../public_html/django2adserver/cgi-bin/delivery/media/')


#MEDIA_URL ='delivery/media/'
MEDIA_URL ='../public_html/pydelivery/media/'
#MEDIA_URL ='../public_html/django2adserver/cgi-bin/delivery/media/'






# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'sd!!!imdmfieaxe+^7bi@lv-00)at(n0a+(n6u5-=bxvt*yuco'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

#ALLOWED_HOSTS = ['139.59.67.0']
#ALLOWED_HOSTS = ['127.0.0.1','localhost','192.168.1.79','192.168.1.80','139.59.67.0','*']
ALLOWED_HOSTS = ['*']


CORS_ORIGIN_ALLOW_ALL  = True 
CORS_ALLOW_CREDENTIALS = False
CORS_ALLOW_METHODS = ['DELETE','GET','OPTIONS','PATCH','POST','PUT']
CORS_ALLOW_HEADERS = ['accept','accept-encoding','Authorization','content-type','dnt','origin','user-agent', 'x-csrftoken','x-requested-with']





# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'inventory',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
    #'django.middleware.csrf.CsrfViewMiddleware',


EMAIL_BACKEND 		= 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST 			= 'mail.onetracky.com'
EMAIL_USE_TLS 		= True
EMAIL_PORT 			= 587
EMAIL_HOST_USER 	= 'support@onetracky.com'
EMAIL_HOST_PASSWORD = 'Q1w2@Jmm@123'



ROOT_URLCONF = 'django2adserver.urls'

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

WSGI_APPLICATION = 'django2adserver.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'onetrack_adserver',
		'USER':'postgres',
		'PASSWORD':'F2X8bXmYYbybnH',
		'HOST':'139.59.67.0',
		'PORT':'5432'
		
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
