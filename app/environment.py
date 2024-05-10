from os import environ

AWS_SECRET_KEY = environ.get("AWS_SECRET_KEY")
AWS_API_KEY = environ.get("AWS_API_KEY")
DATABASE_URI = environ.get("DATABASE_URI")
WEBHOOK_REQUEST_URL = environ.get("WEBHOOK_REQUEST_URL")
WEBHOOK_URL = environ.get("WEBHOOK_URL")
ENV_KEY = environ.get("ENV")
AWS_BUCKET_NAME = environ.get("AWS_BUCKET_NAME")
