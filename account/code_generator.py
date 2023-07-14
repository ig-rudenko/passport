import secrets
import string


def generate_code(length: int = 4) -> str:
    """
    Функция генерирует случайный код заданной длины, используя заглавные буквы и цифры.

    :param length: Длина сгенерированного кода, defaults to 4.
    :return: Случайно сгенерированная строка символов заданной длины.
    """
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))
