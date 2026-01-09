"""User Preference Entity"""
from dataclasses import dataclass

@dataclass
class UserPreference:
    user_id: str
    key: str
    value: str
