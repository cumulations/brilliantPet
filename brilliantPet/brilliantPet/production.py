from brilliantPet.baseSettings import *

# For Production
DEBUG = False
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'brilliantPet',
        'USER': 'root',
        'PASSWORD': 'brilliantpet12#$',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}