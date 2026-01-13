"""
LernsystemX WebSocket Events Package

SocketIO event handlers for real-time features:
- AI Studio progress updates
- LiveRoom communication
- Notifications

Phase D4 - KI-Authoring-Studio WebSocket Integration
"""

from app.sockets.ai_studio_events import register_ai_studio_events


def register_socket_events(socketio):
    """
    Register all SocketIO event handlers

    Args:
        socketio: Flask-SocketIO instance
    """
    register_ai_studio_events(socketio)


__all__ = ['register_socket_events']
