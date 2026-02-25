from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class ScriptBreakdown:
    total_pages: int = 0
    total_scenes: int = 0
    total_characters: int = 0
    scenes: List[str] = field(default_factory=list)
    characters: List[str] = field(default_factory=list)
    character_appearances: Dict[str, int] = field(default_factory=dict)
    character_scenes: Dict[str, List[str]] = field(default_factory=dict)