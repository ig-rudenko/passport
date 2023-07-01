from typing import List

from pydantic import BaseModel


class Secret(BaseModel):
    username: str
    identifier: str
    secret: str


class SecretStatus(BaseModel):
    secret: Secret
    ok: bool
    error: str = ""
