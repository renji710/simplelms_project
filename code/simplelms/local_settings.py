DEBUG = True
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'simple_lms',         
        'USER': 'simple_user',        
        'PASSWORD': 'simple_password',
        'HOST': 'postgres',           
        'PORT': '5432',              
    }
}