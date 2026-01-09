"""SystemFeature Entity"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class SystemFeature:
    """System feature configuration."""
    feature_code: str
    feature_name: str
    enabled: bool = True
    description: Optional[str] = None
    category: Optional[str] = None
    
    def enable(self) -> None:
        self.enabled = True
    
    def disable(self) -> None:
        self.enabled = False
