"""
LernsystemX WebSocket Events Package

SocketIO event handlers for real-time features:
- AI Editor progress updates
- LiveRoom communication
- Notifications

Phase D4 - KI-Authoring-Editor WebSocket Integration
"""

from app.sockets.ai_editor_events import register_ai_editor_events


def register_socket_events(socketio):
    """
    Register all SocketIO event handlers

    Args:
        socketio: Flask-SocketIO instance
    """
    register_ai_editor_events(socketio)


__all__ = ['register_socket_events']
