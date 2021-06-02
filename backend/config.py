import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'very_top_secret_precious_key')

    SQLALCHEMY_DATABASE_URL = "sqlite:///sql_app.db"
    # SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

key = Config.SECRET_KEY
jwt_alg = "HS256"
db_url = Config.SQLALCHEMY_DATABASE_URL

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
API_SERVICE_NAME = 'gmail'
API_VERSION = 'v1'