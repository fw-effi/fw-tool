# URL Settings
URL = "http://localhost:8080"
# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# Serialize objects to ASCII-encoded JSON. If this is disabled, the JSON will be returned as a Unicode string, or encoded as UTF-8 by jsonify.
# This has security implications when rendering the JSON into JavaScript in templates, and should typically remain enabled. 
JSON_AS_ASCII = False

# Define the database - we are working with
# SQLite for this example
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Celery Async Task Queue Settings
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = "secret"

# Secret key for signing cookies
SECRET_KEY = "secret"

# OAuth Settings
OIDC_CLIENT_SECRETS= 'app/mod_auth/client_secret.json'
OIDC_INTROSPECTION_AUTH_METHOD= 'client_secret_post'
OIDC_SCOPES = ['openid','oxd','profile']
OIDC_COOKIE_SECURE = False
OIDC_CLOCK_SKEW = 590
OVERWRITE_REDIRECT_URI = 'http://localhost:8081/auth/callback/lodur'

# Lodur Settings
LODUR_USERNAME = 'andsche'
LODUR_PASSWORD = '9SG2uxqnfhQafwiM3qYT'