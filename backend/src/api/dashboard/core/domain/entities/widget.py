"""Widget Entity"""
from dataclasses import dataclass

@dataclass
class Widget:
    widget_id: int
    type: str
    config: dict
