import pytest

from app.methods.isbn import validate_isbn


class TestISBNValidate:
    @pytest.mark.parametrize(
        "isbn",
        [
            "0-306-40615-2",  # Valid ISBN-10
            "978-0-306-40615-7",  # Valid ISBN-13
            "0-306-40615-3",  # Valid ISBN-10
            "978-0-306-40615-6",  # Valid ISBN-13
        ],
    )
    def test_validate_valid_isbn(self, isbn):
        assert validate_isbn(isbn) is True

    @pytest.mark.parametrize(
        "isbn",
        [
            "123456789012345678901",  # Too long to be valid
            "invalidisbn",  # Non-numeric input
            "",  # Empty input
            None,  # None input
        ],
    )
    def test_validate_invalid_isbn(self, isbn):
        assert validate_isbn(isbn) is False
