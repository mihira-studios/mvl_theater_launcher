# domain/auth_tokens.py
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AuthTokens:
    access_token: str
    refresh_token: str | None
    expires_at: datetime  # UTC
