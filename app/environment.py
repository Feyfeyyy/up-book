from os import environ

SECRET_KEY = environ.get("SECRET_KEY")
API_KEY = environ.get("API_KEY")
DATABASE_URI = environ.get("DATABASE_URI")
WEBHOOK_REQUEST_URL = environ.get("WEBHOOK_REQUEST_URL")
WEBHOOK_URL = environ.get("WEBHOOK_URL")
