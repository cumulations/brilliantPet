from brilliantPet.baseSettings import *

# For Development
DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'brilliantPet',
        'USER': 'root',
        # 'PASSWORD': 'root1234',
        'PASSWORD' : "password",
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
