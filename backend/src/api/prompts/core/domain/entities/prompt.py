"""Prompt Entity"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Prompt:
    prompt_id: int
    name: str
    template: str
    category: Optional[str] = None
