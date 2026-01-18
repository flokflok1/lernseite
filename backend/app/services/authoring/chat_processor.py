"""
Chat Message Processing for Authoring Service

Handles:
- Chat message processing
- AI prompt building and execution
- Response parsing
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.services.ai_adapter import AIAdapter, AIProviderError
from app.services.file_context_service import FileContextService
from app.domain.ai.configuration.prompts.authoring import get_authoring_prompt

from .exceptions import AuthoringServiceError
from .session_manager import SessionManager
from .helpers import ContextHelper, ConversationHelper, JSONHelper

logger = logging.getLogger(__name__)


class ChatProcessor:
    """Process chat messages and generate AI responses."""

    def __init__(self, provider: str = "anthropic", model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize chat processor.

        Args:
            provider: AI provider (anthropic, openai)
            model: Model identifier
        """
        self.provider = provider
        self.model = model

    def process_message(
        self,
        course_id: str,
        context_type: str,
        context_id: Optional[str],
        message: str,
        file_context: List[str],
        session_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message and generate AI response.

        Args:
            course_id: Course UUID
            context_type: Type of content (chapter, lesson, task, learning_method)
            context_id: Existing content ID (None for new creation)
            message: User message
            file_context: List of file IDs for context
            session_id: Chat session ID
            user_id: Optional user ID

        Returns:
            Dict with AI response and optional generated content

        Raises:
            AuthoringServiceError: If processing fails
        """
        start_time = datetime.utcnow()

        # Get or create session
        session = SessionManager.get_or_create_session(session_id)
        session['course_id'] = course_id
        session['context_type'] = context_type
        session['context_id'] = context_id
        session['file_context'] = file_context

        # Add user message to history
        SessionManager.add_message(session_id, 'user', message)

        try:
            # Get file context if provided
            file_context_text = ""
            if file_context:
                file_context_text = FileContextService.extract_for_ai_context(
                    file_context, context_type
                )

            # Get course/chapter/lesson info for context
            context_info = ContextHelper.get_context_info(course_id, context_type, context_id)

            # Build prompt
            prompt_context = {
                'context_type': context_type,
                'context_id': context_id,
                'course_info': context_info.get('course', {}),
                'chapter_info': context_info.get('chapter', {}),
                'lesson_info': context_info.get('lesson', {}),
                'file_context': file_context_text,
                'conversation_history': ConversationHelper.format_history(
                    session['messages'][:-1]
                ),
                'user_message': message
            }

            # Get system prompt based on context type
            system_prompt = get_authoring_prompt(context_type, 'system')
            user_prompt = get_authoring_prompt(context_type, 'user').format(**prompt_context)

            # Build messages for AI
            messages = [{'role': 'system', 'content': system_prompt}]

            # Add conversation history (last 10 messages)
            history = session['messages'][-11:-1]  # Exclude current message
            for msg in history:
                messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })

            messages.append({'role': 'user', 'content': user_prompt})

            # Call AI
            adapter = AIAdapter(provider=self.provider, model=self.model)
            result = adapter.send_messages(
                messages=messages,
                temperature=0.7,
                max_tokens=4000
            )

            output_text = result.get('output_text', '')

            # Parse response for content
            generated_content = None
            response_text = output_text

            # Check if response contains JSON content
            if '```json' in output_text or output_text.strip().startswith('{'):
                json_match = JSONHelper.extract_json(output_text)
                if json_match:
                    generated_content = json_match
                    session['generated_content'] = generated_content
                    # Remove JSON from response text for display
                    response_text = JSONHelper.extract_text_before_json(output_text)

            # Add AI response to history
            SessionManager.add_message(
                session_id,
                'assistant',
                response_text,
                generated_content
            )

            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            return {
                'success': True,
                'session_id': session['session_id'],
                'response': response_text,
                'generated_content': generated_content,
                'has_content': generated_content is not None,
                'tokens_used': result.get('total_tokens', 0),
                'cost_eur': result.get('cost_eur', 0),
                'processing_time_ms': processing_time
            }

        except AIProviderError as e:
            logger.error(f"AI provider error: {str(e)}")
            raise AuthoringServiceError(f"AI generation failed: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}")
            raise AuthoringServiceError(f"Processing failed: {str(e)}")
