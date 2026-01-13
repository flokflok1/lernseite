"""
LernsystemX Dashboard Widgets - Request Models

Pydantic models for widget API requests.

ISO 27001:2013 compliant - Widget API models
"""

from pydantic import BaseModel
from typing import Optional, Dict


class AddWidgetRequest(BaseModel):
    """Request model for adding widget"""
    widget_key: str
    layout_id: Optional[str] = None
    position_x: int = 0
    position_y: int = 0
    width: int = 2
    height: int = 1
    custom_settings: Optional[Dict] = None


class UpdatePositionRequest(BaseModel):
    """Request model for updating widget position"""
    position_x: int
    position_y: int
    width: Optional[int] = None
    height: Optional[int] = None


class UpdateSettingsRequest(BaseModel):
    """Request model for updating widget settings"""
    custom_settings: Dict
