from flask_session import Session

from app import app

if __name__ == "__main__":
    Session(app)
    app.run()
