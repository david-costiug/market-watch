from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Entity:
    platform_source: str
    name: str
    city: str | None
    type: str
