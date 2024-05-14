import factory
from factory.alchemy import SQLAlchemyModelFactory

from app import db
from app.models import Account, Book, Buckets, Publisher


class AccountFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Account
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "flush"

    email = factory.Faker("email")
    password = factory.Faker("password")


class BookFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Book
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "flush"

    title = factory.Faker("word")
    isbn = factory.Faker("isbn13")

    @factory.lazy_attribute
    def account(self):
        return AccountFactory()


class PublisherFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Publisher
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "flush"

    author = factory.Faker("name")
    publisher_name = factory.Faker("company")
    publisher_date = factory.Faker("date")

    @factory.lazy_attribute
    def book(self):
        return BookFactory()


class BucketsFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Buckets
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "flush"

    bucket_name = factory.Faker("word")
    file_name = factory.Faker("file_name")
    file_path = factory.Faker("file_path")

    @factory.lazy_attribute
    def account(self):
        return AccountFactory()
