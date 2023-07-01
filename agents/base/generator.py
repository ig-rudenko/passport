import secrets
import string
from abc import ABC, abstractmethod

from .secret import Secret, SecretStatus


class GeneratorException(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class BaseGenerator(ABC):
    @abstractmethod
    def regenerate(self, secret: Secret) -> SecretStatus:
        pass

    @staticmethod
    def generate_secret(length: int, symbols: bool):
        # create a list of possible characters
        chars = string.ascii_letters + string.digits
        if symbols:
            chars += string.punctuation

        # randomly choose characters from the list
        password = ""
        for i in range(length):
            password += secrets.choice(chars)

        # return the password
        return password
