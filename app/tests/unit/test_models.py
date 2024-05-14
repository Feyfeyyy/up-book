import hashlib

from app.tests.factories import (
    AccountFactory,
    BookFactory,
    BucketsFactory,
    PublisherFactory,
)


class TestAccountModel:
    def test_account_model_init(self):
        email = "test@example.com"
        password = "password123"

        # Create an instance of the Account model
        account = AccountFactory(email=email, password=password)

        # Assert that the attributes are set correctly
        assert account.email == email
        assert account.password == hashlib.md5(password.encode()).hexdigest()


class TestBookModel:
    def test_book_model_init(self):
        title = "Test Book"
        isbn = "1234567890"

        # Create an instance of the Book model
        book = BookFactory(title=title, isbn=isbn)

        # Assert that the attributes are set correctly
        assert book.title == title
        assert book.isbn == isbn
        assert book.account_id is not None


class TestPublisherModel:
    def test_publisher_model_init(self):
        author = "John Doe"
        publisher_name = "Publisher A"
        publisher_date = "2021-01-01"

        # Create an instance of the Publisher model
        publisher = PublisherFactory(
            author=author, publisher_name=publisher_name, publisher_date=publisher_date
        )

        # Assert that the attributes are set correctly
        assert publisher.books_id is not None
        assert publisher.author == author
        assert publisher.publisher_name == publisher_name
        assert publisher.publisher_date == publisher_date


class TestBucketsModel:
    def test_buckets_model_init(self):
        bucket_name = "test_bucket"
        file_name = "test_file"
        file_path = "/path/to/file"

        # Create an instance of the Buckets model
        bucket = BucketsFactory(
            bucket_name=bucket_name, file_name=file_name, file_path=file_path
        )

        # Assert that the attributes are set correctly
        assert bucket.bucket_name == bucket_name
        assert bucket.file_name == file_name
        assert bucket.file_path == file_path
        assert bucket.account_id is not None
