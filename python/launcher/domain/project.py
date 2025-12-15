# domain/project.py
from dataclasses import dataclass


@dataclass
class Project:
    id: str
    name: str
    code: str
    description: str | None = None
    version: str | None = None
