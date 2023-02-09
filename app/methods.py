def validate_isbn(isbn: str) -> bool:
    """
    Validate ISBN-10 number. Returns True if valid, False otherwise.
    """
    isbn = isbn.replace("-", "")
    if len(isbn) != 10:
        return False
    sums = 0
    for i in range(10):
        if isbn[i].isdigit():
            sums += int(isbn[i]) * (10 - i)
        elif isbn[i] == "X" and i == 9:
            sums += 10
        else:
            return False
    return sums % 11 == 0
