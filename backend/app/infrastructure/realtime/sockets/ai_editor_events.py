"""
LernsystemX AI Editor WebSocket Events

Real-time event handlers for KI-Authoring-Editor:
- Session progress updates
- Generation status
- Error notifications

Phase D4 - KI-Authoring-Editor WebSocket Integration
"""

from flask import request
from flask_socketio import emit, join_room, leave_room, Namespace
from flask_jwt_extended import decode_token
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class AIEditorNamespace(Namespace):
    """
    AI Editor WebSocket Namespace

    Handles all real-time events for KI-Authoring-Editor sessions.
    Uses rooms for session-specific updates.
    """

    def __init__(self, namespace='/ai-editor'):
        super().__init__(namespace)
        self.connected_users = {}  # sid -> user_id mapping

    def on_connect(self):
        """
        Handle client connection

        Validates JWT token from auth query parameter.
        """
        try:
            # Get token from query params or headers
            token = request.args.get('token')
            if not token:
                logger.warning('AI Editor WebSocket connection without token')
                return False

            # Validate token
            decoded = decode_token(token)
            user_id = decoded.get('sub')

            if not user_id:
                logger.warning('AI Editor WebSocket: Invalid token - no user_id')
                return False

            # Store user mapping
            self.connected_users[request.sid] = user_id
            logger.info(f'AI Editor WebSocket connected: user={user_id}, sid={request.sid}')

            emit('connected', {
                'status': 'connected',
                'user_id': user_id,
                'message': 'Connected to AI Editor'
            })

            return True

        except Exception as e:
            logger.error(f'AI Editor WebSocket connection error: {str(e)}')
            return False

    def on_disconnect(self):
        """Handle client disconnection"""
        sid = request.sid
        user_id = self.connected_users.pop(sid, None)
        logger.info(f'AI Editor WebSocket disconnected: user={user_id}, sid={sid}')

    def on_join_session(self, data):
        """
        Join a session room to receive updates

        Args:
            data: { session_id: string }
        """
        session_id = data.get('session_id')
        if not session_id:
            emit('error', {'message': 'session_id required'})
            return

        user_id = self.connected_users.get(request.sid)
        room = f'session:{session_id}'

        join_room(room)
        logger.info(f'User {user_id} joined session room: {room}')

        emit('joined_session', {
            'session_id': session_id,
            'message': f'Joined session {session_id}'
        })

    def on_leave_session(self, data):
        """
        Leave a session room

        Args:
            data: { session_id: string }
        """
        session_id = data.get('session_id')
        if not session_id:
            return

        room = f'session:{session_id}'
        leave_room(room)

        emit('left_session', {
            'session_id': session_id,
            'message': f'Left session {session_id}'
        })

    def on_ping(self, data=None):
        """Handle ping for keepalive"""
        emit('pong', {'timestamp': data.get('timestamp') if data else None})


def register_ai_editor_events(socketio):
    """
    Register AI Editor namespace and events

    Args:
        socketio: Flask-SocketIO instance
    """
    socketio.on_namespace(AIEditorNamespace('/ai-editor'))
    logger.info('AI Editor WebSocket namespace registered: /ai-editor')


# ============================================================================
# Utility Functions for Emitting Events from API Routes
# ============================================================================

def emit_generation_progress(socketio, session_id: str, progress: int, step: str, message: str, data: dict = None):
    """
    Emit generation progress update to session room

    Args:
        socketio: Flask-SocketIO instance
        session_id: Session UUID
        progress: Progress percentage (0-100)
        step: Current step name
        message: Human-readable status message
        data: Additional data (optional)
    """
    room = f'session:{session_id}'
    event_data = {
        'session_id': session_id,
        'event_type': 'progress',
        'step': step,
        'progress': progress,
        'message': message,
        'data': data or {}
    }

    socketio.emit('generation_progress', event_data, room=room, namespace='/ai-editor')
    logger.debug(f'Emitted progress to {room}: {progress}% - {message}')


def emit_generation_complete(socketio, session_id: str, step: str, result: dict):
    """
    Emit generation complete event

    Args:
        socketio: Flask-SocketIO instance
        session_id: Session UUID
        step: Completed step name
        result: Generation result data
    """
    room = f'session:{session_id}'
    event_data = {
        'session_id': session_id,
        'event_type': 'complete',
        'step': step,
        'progress': 100,
        'message': f'{step} generation complete',
        'data': result
    }

    socketio.emit('generation_complete', event_data, room=room, namespace='/ai-editor')
    logger.info(f'Generation complete for session {session_id}, step {step}')


def emit_generation_error(socketio, session_id: str, step: str, error: str, details: dict = None):
    """
    Emit generation error event

    Args:
        socketio: Flask-SocketIO instance
        session_id: Session UUID
        step: Failed step name
        error: Error message
        details: Additional error details (optional)
    """
    room = f'session:{session_id}'
    event_data = {
        'session_id': session_id,
        'event_type': 'error',
        'step': step,
        'progress': 0,
        'message': error,
        'data': details or {}
    }

    socketio.emit('generation_error', event_data, room=room, namespace='/ai-editor')
    logger.error(f'Generation error for session {session_id}: {error}')


def emit_session_status_changed(socketio, session_id: str, old_status: str, new_status: str):
    """
    Emit session status change event

    Args:
        socketio: Flask-SocketIO instance
        session_id: Session UUID
        old_status: Previous status
        new_status: New status
    """
    room = f'session:{session_id}'
    event_data = {
        'session_id': session_id,
        'event_type': 'status_changed',
        'old_status': old_status,
        'new_status': new_status,
        'message': f'Session status changed to {new_status}'
    }

    socketio.emit('session_status', event_data, room=room, namespace='/ai-editor')
    logger.info(f'Session {session_id} status changed: {old_status} -> {new_status}')


def emit_variant_generated(socketio, session_id: str, variant_type: str, variant_index: int, variant_id: str):
    """
    Emit new variant generated event

    Args:
        socketio: Flask-SocketIO instance
        session_id: Session UUID
        variant_type: Type of variant (theory, lesson, method, etc.)
        variant_index: Index of the variant
        variant_id: UUID of the generated variant
    """
    room = f'session:{session_id}'
    event_data = {
        'session_id': session_id,
        'event_type': 'variant_generated',
        'variant_type': variant_type,
        'variant_index': variant_index,
        'variant_id': variant_id,
        'message': f'New {variant_type} variant generated'
    }

    socketio.emit('variant_generated', event_data, room=room, namespace='/ai-editor')
    logger.debug(f'Variant generated: {variant_type}[{variant_index}] for session {session_id}')
