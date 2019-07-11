# URL Settings
URL = "http://localhost:8080"
# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# Define the database - we are working with
# SQLite for this example
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

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
OVERWRITE_REDIRECT_URI = 'http://dev.test:8080/auth/callback/lodur'