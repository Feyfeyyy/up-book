import re


def validate_isbn(isbn: str) -> bool:
    """
    Validate ISBN-10 and ISBN-13 numbers.

    :param isbn: ISBN number to validate
    :return: True if valid, False otherwise
    """
    # Regex to check valid ISBN Code
    regex = "^(?=(?:[^0-9]*[0-9]){10}(?:(?:[^0-9]*[0-9]){3})?$)[\\d-]+$"

    # Compile the ReGex
    p = re.compile(regex)

    # If the string is empty
    # return false
    if isbn is None:
        return False

    # Return if the string
    # matched the ReGex
    if re.search(p, isbn):
        return True
    else:
        return False
