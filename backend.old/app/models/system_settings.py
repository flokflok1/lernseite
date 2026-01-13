"""
LernsystemX Pydantic Models - System Settings

Validation models for system settings API.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Literal, Dict, Any


class SwitchModeRequest(BaseModel):
    """Request to switch system mode/environment"""
    mode: Literal['development', 'production'] = Field(
        ...,
        description="Target environment mode"
    )

    @validator('mode')
    def validate_mode(cls, v):
        """Validate mode value"""
        if v not in ['development', 'production']:
            raise ValueError("Mode must be 'development' or 'production'")
        return v


class MaintenanceModeRequest(BaseModel):
    """Request to toggle maintenance mode"""
    enabled: bool = Field(
        ...,
        description="Enable or disable maintenance mode"
    )
    message: Optional[str] = Field(
        None,
        max_length=500,
        description="Custom maintenance message shown to users"
    )


class UpdateSettingRequest(BaseModel):
    """Request to update a single setting"""
    value: str = Field(
        ...,
        description="New setting value"
    )
    value_type: Optional[Literal['string', 'number', 'boolean', 'json']] = Field(
        'string',
        description="Type of the value"
    )


class SystemStatusResponse(BaseModel):
    """System status response"""
    environment: str = Field(..., description="Current environment (dev/prod)")
    debug_enabled: bool = Field(..., description="Debug mode status")
    maintenance_mode: bool = Field(..., description="Maintenance mode status")
    uptime_seconds: int = Field(..., description="System uptime in seconds")
    version: str = Field(..., description="System version")
    database_connected: bool = Field(..., description="Database connection status")
    redis_connected: bool = Field(..., description="Redis connection status")


class SettingResponse(BaseModel):
    """Single setting response"""
    setting_id: int
    key: str
    value: Any
    value_type: str
    category: Optional[str]
    description: Optional[str]
    editable: bool
    encrypted: bool
    created_at: str
    updated_at: str
