def validate_isbn(isbn: str) -> bool:
    """
    Validate ISBN-10 and ISBN-13 numbers.

    :param isbn: ISBN number to validate
    :return: True if valid, False otherwise
    """
    # Remove hyphens and whitespace from the input ISBN
    isbn = isbn.replace("-", "").replace(" ", "")

    if len(isbn) == 10:
        # ISBN-10 validation
        if not isbn[:-1].isdigit() or (isbn[-1] != 'X' and not isbn[-1].isdigit()):
            return False
        check = sum((i + 1) * int(digit) for i, digit in enumerate(isbn[:-1])) % 11
        check = 'X' if check == 10 else str(check)
        return isbn[-1] == check
    elif len(isbn) == 13:
        # ISBN-13 validation
        if not isbn.isdigit():
            return False
        check = (10 - sum(int(digit) * (3 if i % 2 else 1) for i, digit in enumerate(isbn[:-1]))) % 10
        return int(isbn[-1]) == check
    else:
        return False
