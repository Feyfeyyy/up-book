from app import app
from flask_session import Session

if __name__ == "__main__":
    Session(app)
    app.run()
