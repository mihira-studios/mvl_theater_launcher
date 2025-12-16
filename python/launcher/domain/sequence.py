# domain/project.py
from dataclasses import dataclass


@dataclass
class Sequence:
    id: str
    project_id: str
    name: str
    code: str
    status: str
    meta: dict