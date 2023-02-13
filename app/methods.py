def validate_isbn(isbn: str) -> bool:
    """
    Validate ISBN-10 and ISBN-13 numbers.

    :param isbn: ISBN number
    :return: True if valid, False otherwise
    """
    isbn = isbn.replace("-", "")
    if len(isbn) == 10:
        # ISBN-10 validation
        if not isbn.isdigit():
            return False
        sums = 0
        for i in range(9):
            sums += (i + 1) * int(isbn[i])
        check = sums % 11
        if check == 10:
            check = "X"
        else:
            check = str(check)
        if isbn[9] != check:
            return False
        return True
    elif len(isbn) == 13:
        # ISBN-13 validation
        if not isbn.isdigit():
            return False
        sums = 0
        for i in range(12):
            if (i + 1) % 2 == 0:
                sums += 3 * int(isbn[i])
            else:
                sums += int(isbn[i])
        check = 10 - (sums % 10)
        if check == 10:
            check = 0
        if int(isbn[12]) != check:
            return False
        return True
    else:
        return False
