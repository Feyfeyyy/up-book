import hashlib

from app import db


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    created_date = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, email, password):
        self.email = email
        self.password = hashlib.md5(password.encode()).hexdigest()


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    isbn = db.Column(db.String(255), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    created_date = db.Column(db.DateTime, server_default=db.func.now())
    account = db.relationship("Account", backref=db.backref("books", lazy=True))

    def __init__(self, title, isbn, account_id):
        self.title = title
        self.isbn = isbn
        self.account_id = account_id


class Publisher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    books_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    publisher_name = db.Column(db.String(255), nullable=False)
    publisher_date = db.Column(db.String(255), nullable=False)
    book = db.relationship("Book", backref=db.backref("publishers", lazy=True))

    def __init__(self, books_id, author, publisher_name, publisher_date):
        self.books_id = books_id
        self.author = author
        self.publisher_name = publisher_name
        self.publisher_date = publisher_date


class Buckets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bucket_name = db.Column(db.String(255), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    uploaded_date = db.Column(db.DateTime, server_default=db.func.now())
    account = db.relationship("Account", backref=db.backref("aws_s3", lazy=True))

    def __init__(self, bucket_name, file_name, file_path, account_id):
        self.bucket_name = bucket_name
        self.file_name = file_name
        self.file_path = file_path
        self.account_id = account_id
