from dataclasses import dataclass
from typing import Optional


@dataclass
class Entity:
    platform_source: str
    name: str
    city: Optional[str]
    type: str
