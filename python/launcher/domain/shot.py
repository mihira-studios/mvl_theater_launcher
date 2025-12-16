# domain/project.py
from dataclasses import dataclass


@dataclass
class Shot:
    id: str
    project_id: str
    sequence_id: str
    name: str
    code: str
    status: str
    meta: dict