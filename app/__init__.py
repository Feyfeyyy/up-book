from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate

from app.extensions import db

load_dotenv(".env")
app = Flask(__name__)
app.config.from_pyfile("environment.py")
app.app_context().push()

if app.config["ENV_KEY"] == "production":
    app.config.from_object("config.ProductionConfig")
elif app.config["ENV_KEY"] == "testing":
    app.config.from_object("config.TestingConfig")
elif app.config["ENV_KEY"] == "development":
    app.config.from_object("config.DevelopmentConfig")

db.init_app(app)
migrate = Migrate(app, db)

from app import views
