import os
import sys

# Statement for enabling the development environment
DEBUG = True

# Define the application directory
BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))

# Default Sender for flask-mail
MAIL_DEFAULT_SENDER = ('Alex', 'alexdonnellan71@gmail.com')
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = 'alexdonnellan71@gmail.com'
MAIL_PASSWORD = 'Ad07032003'
MAIL_SUPPRESS_SEND = True

# Secret key for signing cookies
SECRET_KEY = b',chks\x9f|\x08\x94c-\x94\x90\xa5\xa2\xbd'
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False