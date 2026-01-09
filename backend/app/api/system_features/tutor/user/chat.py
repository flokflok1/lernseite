"""
Tutor User Chat Endpoint (DDD)

User-facing chat endpoint with context-aware AI tutoring.
Uses TutorSessionFactory, TutorContext, and TutorKnowledgeService.
"""

from flask import request, jsonify, g
from typing import Dict, Any, Tuple, Optional
import logging

from app.extensions import limiter
from app.middleware.auth import token_required
from app.services.ai_adapter import AIAdapter

from app.api.system_features.tutor.core import (
    TutorSessionFactory,
    TutorKnowledgeService,
    TutorContext
)
from app.api.system_features.tutor.core.events import (
    TutorSessionStartedEvent,
    EventPublisher,
    EventPriority
)

from . import tutor_user_chat_bp

logger = logging.getLogger(__name__)


# Default system prompt for the tutor
DEFAULT_TUTOR_PROMPT = """Du bist ein freundlicher und hilfreicher KI-Tutor auf LernsystemX.
Du begleitest Lernende durch ihre Lernreise und hilfst bei Fragen zu Kursen und Lernmethoden.
Du bist geduldig, ermutigend und erklärst Konzepte klar und verständlich.
Antworte immer auf Deutsch, es sei denn der User spricht eine andere Sprache.
Halte deine Antworten prägnant aber hilfreich - idealerweise 2-4 Sätze.

Wenn der User Fragen zum aktuellen Lerninhalt hat, beziehe dich auf den bereitgestellten Kurs-Kontext.
Du kannst Konzepte erklären, Beispiele geben und bei Übungen helfen."""


@tutor_user_chat_bp.route('/chat', methods=['POST'])
@token_required
@limiter.limit("30 per minute")
def tutor_chat() -> Tuple[Dict[str, Any], int]:
    """
    Chat with the AI Tutor (context-aware).

    Request Body:
        message (str): User's message
        context (str): Page context (optional)
        systemPrompt (str): Custom system prompt (optional)
        history (list): Chat history (optional, max 10 messages)
        courseId (str): Current course ID (optional)
        chapterId (str): Current chapter ID (optional)
        lessonId (int): Current lesson ID (optional)
        methodId (str): Current learning method ID (optional)

    Returns:
        JSON response with tutor message, tokens used, context status

    DDD: Uses TutorSessionFactory, TutorContext, TutorKnowledgeService
    """
    try:
        user_id = g.current_user['user_id']
        data = request.get_json()

        if not data or not data.get('message'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Message is required'
                }
            }), 400

        message = data['message']
        page_context = data.get('context', '')
        custom_system_prompt = data.get('systemPrompt', DEFAULT_TUTOR_PROMPT)
        history = data.get('history', [])

        # DDD: Create TutorContext value object
        context = TutorContext(
            user_id=user_id,
            course_id=data.get('courseId'),
            chapter_id=data.get('chapterId'),
            lesson_id=data.get('lessonId'),
            method_id=data.get('methodId'),
            page_context=page_context
        )

        # DDD: Use Factory to create session
        session = TutorSessionFactory.create_chat_session(
            user_id=user_id,
            message=message,
            context=context,
            history=history
        )

        # Build knowledge context using Service
        knowledge_context = ''
        context_used = False

        if context.has_course_context():
            knowledge_context = TutorKnowledgeService.build_context_for_chat(
                context=context,
                include_files=True,
                include_progress=True
            )
            if knowledge_context and knowledge_context != "Kein spezifischer Kurs-Kontext verfügbar.":
                context_used = True
                logger.debug(f"Loaded tutor context for course={context.course_id}, chapter={context.chapter_id}")

        # Build the full system prompt with context
        system_prompt = custom_system_prompt

        # Add page context (where user is in the app)
        if page_context:
            system_prompt += f"\n\nAktueller Seitenkontext: {page_context}"

        # Add knowledge context from DB (course/chapter/lesson content)
        if knowledge_context:
            system_prompt += f"\n\n{knowledge_context}"

        # Build messages for the AI
        messages = []

        # Add history (limit already applied by factory)
        for msg in session['history']:
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })

        # Add current message
        messages.append({
            'role': 'user',
            'content': message
        })

        # Call AI
        response = AIAdapter.chat_completion(
            messages=messages,
            system_prompt=system_prompt,
            model='gpt-4o-mini',  # Use fast model for chat
            max_tokens=800 if context_used else 500,  # More tokens when using context
            temperature=0.7,
            user_id=user_id
        )

        # DDD: Publish Domain Event
        event = TutorSessionStartedEvent(
            event_id=session['session_id'],
            occurred_at=session['created_at'],
            aggregate_id=user_id,
            user_id=user_id,
            has_context=context_used,
            tokens_used=response.get('usage', {}).get('total_tokens', 0),
            priority=EventPriority.LOW
        )
        EventPublisher.publish(event)

        return jsonify({
            'success': True,
            'data': {
                'message': response.get('content', ''),
                'tokens_used': response.get('usage', {}).get('total_tokens', 0),
                'context_used': context_used,
                'session_id': session['session_id']
            }
        }), 200

    except Exception as e:
        logger.error(f"Tutor chat error: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'CHAT_ERROR',
                'message': str(e)
            }
        }), 500
