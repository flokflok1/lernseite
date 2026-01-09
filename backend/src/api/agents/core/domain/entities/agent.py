"""Agent Entity"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Agent:
    agent_id: str
    name: str
    type: str
    active: bool = True
