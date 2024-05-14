import hashlib

from app import db


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_date = db.Column(db.DateTime, server_default=db.func.now())

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, password):
        self.password_hash = hashlib.md5(password.encode()).hexdigest()


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    isbn = db.Column(db.String(255), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    created_date = db.Column(db.DateTime, server_default=db.func.now())
    account = db.relationship("Account", backref=db.backref("books", lazy=True))


class Publisher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    books_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    publisher_name = db.Column(db.String(255), nullable=False)
    publisher_date = db.Column(db.String(255), nullable=False)
    book = db.relationship("Book", backref=db.backref("publishers", lazy=True))


class Buckets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bucket_name = db.Column(db.String(255), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    uploaded_date = db.Column(db.DateTime, server_default=db.func.now())
    account = db.relationship("Account", backref=db.backref("aws_s3", lazy=True))
