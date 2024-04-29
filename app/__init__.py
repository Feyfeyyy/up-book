from dotenv import load_dotenv
from flask import Flask

load_dotenv(".env")
app = Flask(__name__)
app.config.from_pyfile("environment.py")

if app.config["ENV_KEY"] == "production":
    app.config.from_object("config.ProductionConfig")
elif app.config["ENV_KEY"] == "testing":
    app.config.from_object("config.TestingConfig")
elif app.config["ENV_KEY"] == "development":
    app.config.from_object("config.DevelopmentConfig")

from app import views
