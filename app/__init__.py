from flask import Flask
from dotenv import load_dotenv

load_dotenv('.env')
app = Flask(__name__)
app.config.from_pyfile('environment.py')

if app.config["ENV"] == "production":
    app.config.from_object("config.ProductionConfig")
elif app.config["ENV"] == "testing":
    app.config.from_object("config.TestingConfig")
elif app.config["ENV"] == "development":
    app.config.from_object("config.DevelopmentConfig")

from app import views
