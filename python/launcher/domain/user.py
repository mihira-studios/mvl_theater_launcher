# domain/user.py
from dataclasses import dataclass


@dataclass
class User:
    id: str
    email: str
    display_name: str | None = None
