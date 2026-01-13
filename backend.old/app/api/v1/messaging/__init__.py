"""
Messaging API Package

Blueprints (must be registered with api_v1):
- dm_bp - Direct Messages - /messaging/dm
- group_chat_bp - Group Chat - /messaging/groups

Registration: Blueprints are registered in app/api/__init__.py after api_v1 creation.
"""

from app.api.messaging.direct_messages import dm_bp
from app.api.messaging.group_chat import group_chat_bp

__all__ = ['dm_bp', 'group_chat_bp']
