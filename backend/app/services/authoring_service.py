"""
LernsystemX Authoring Service

Universal chat-based content creation service for KI-Authoring-Studio:
- Chat-based AI interaction
- Chapter, lesson, task, learning method creation
- File context integration
- Preview generation

Phase D4 - Universal KI-Authoring-System
"""

import json
import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.services.ai_adapter import AIAdapter, AIProviderError
from app.services.file_context_service import FileContextService
from app.ki.prompts.authoring_prompts import get_authoring_prompt, QUICK_PROMPTS

logger = logging.getLogger(__name__)


class AuthoringServiceError(Exception):
    """Base exception for authoring service errors"""
    pass


class AuthoringService:
    """
    Universal Authoring Service for chat-based content creation.

    Supports creation of:
    - Chapters with theory
    - Lessons with explanations
    - Tasks/exercises
    - Learning method instances (LM00-LM32)

    Usage:
        >>> service = AuthoringService()
        >>> result = service.process_chat_message(
        ...     course_id="uuid",
        ...     context_type="chapter",
        ...     context_id=None,
        ...     message="Erstelle ein Kapitel über Netzwerktechnik",
        ...     file_context=["file_id_1"],
        ...     session_id="uuid"
        ... )
    """

    # Chat session storage (in production, use Redis)
    _sessions: Dict[str, Dict] = {}

    def __init__(self, provider: str = "anthropic", model: str = "claude-3-5-sonnet-20241022"):
        """Initialize authoring service."""
        self.provider = provider
        self.model = model

    @classmethod
    def get_or_create_session(cls, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get existing session or create new one."""
        if session_id and session_id in cls._sessions:
            return cls._sessions[session_id]

        new_session_id = session_id or str(uuid.uuid4())
        session = {
            'session_id': new_session_id,
            'created_at': datetime.utcnow().isoformat(),
            'messages': [],
            'context_type': None,
            'context_id': None,
            'course_id': None,
            'generated_content': None,
            'file_context': []
        }
        cls._sessions[new_session_id] = session
        return session

    @classmethod
    def get_session(cls, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID."""
        return cls._sessions.get(session_id)

    @classmethod
    def update_session(cls, session_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update session data."""
        if session_id not in cls._sessions:
            raise AuthoringServiceError(f"Session not found: {session_id}")

        session = cls._sessions[session_id]
        session.update(updates)
        return session

    def process_chat_message(
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
        """
        start_time = datetime.utcnow()

        # Get or create session
        session = self.get_or_create_session(session_id)
        session['course_id'] = course_id
        session['context_type'] = context_type
        session['context_id'] = context_id
        session['file_context'] = file_context

        # Add user message to history
        session['messages'].append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.utcnow().isoformat()
        })

        try:
            # Get file context if provided
            file_context_text = ""
            if file_context:
                file_context_text = FileContextService.extract_for_ai_context(
                    file_context, context_type
                )

            # Get course/chapter/lesson info for context
            context_info = self._get_context_info(course_id, context_type, context_id)

            # Build prompt
            prompt_context = {
                'context_type': context_type,
                'context_id': context_id,
                'course_info': context_info.get('course', {}),
                'chapter_info': context_info.get('chapter', {}),
                'lesson_info': context_info.get('lesson', {}),
                'file_context': file_context_text,
                'conversation_history': self._format_conversation_history(session['messages'][:-1]),
                'user_message': message
            }

            # Get system prompt based on context type
            system_prompt = get_authoring_prompt(context_type, 'system')
            user_prompt = get_authoring_prompt(context_type, 'user').format(**prompt_context)

            # Build messages for AI
            messages = [
                {'role': 'system', 'content': system_prompt}
            ]

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
                try:
                    json_match = self._extract_json(output_text)
                    if json_match:
                        generated_content = json_match
                        session['generated_content'] = generated_content
                        # Remove JSON from response text for display
                        response_text = self._extract_text_before_json(output_text)
                except json.JSONDecodeError:
                    pass

            # Add AI response to history
            session['messages'].append({
                'role': 'assistant',
                'content': response_text,
                'timestamp': datetime.utcnow().isoformat(),
                'generated_content': generated_content is not None
            })

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

    def generate_preview(
        self,
        content_type: str,
        generated_content: Dict[str, Any],
        format_type: str = 'html'
    ) -> Dict[str, Any]:
        """
        Generate preview of content without saving.

        Args:
            content_type: Type of content (chapter_theory, lesson_explanation, etc.)
            generated_content: Generated content data
            format_type: Output format (html, markdown)

        Returns:
            Dict with preview HTML/Markdown
        """
        if content_type == 'chapter_theory':
            return self._preview_chapter_theory(generated_content, format_type)
        elif content_type == 'lesson_explanation':
            return self._preview_lesson_explanation(generated_content, format_type)
        elif content_type == 'task':
            return self._preview_task(generated_content, format_type)
        elif content_type == 'learning_method':
            return self._preview_learning_method(generated_content, format_type)
        else:
            return {
                'preview': json.dumps(generated_content, indent=2, ensure_ascii=False),
                'format': 'json'
            }

    def save_content(
        self,
        content_type: str,
        content_id: Optional[str],
        content_data: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Save generated content to database.

        Args:
            content_type: Type of content
            content_id: Existing content ID (None for new)
            content_data: Content to save
            user_id: User ID

        Returns:
            Dict with saved content info
        """
        if content_type == 'chapter':
            return self._save_chapter(content_data, user_id)
        elif content_type == 'chapter_theory':
            return self._save_chapter_theory(content_data, user_id)
        elif content_type == 'lesson':
            return self._save_lesson(content_data, user_id)
        elif content_type == 'lesson_explanation':
            return self._save_lesson_explanation(content_data, user_id)
        elif content_type == 'task':
            return self._save_task(content_data, user_id)
        elif content_type == 'learning_method':
            return self._save_learning_method(content_data, user_id)
        else:
            raise AuthoringServiceError(f"Unknown content type: {content_type}")

    def get_quick_prompts(self, context_type: str) -> List[Dict[str, str]]:
        """Get quick prompts for a context type."""
        return QUICK_PROMPTS.get(context_type, QUICK_PROMPTS.get('general', []))

    # === Private Methods ===

    def _get_context_info(
        self,
        course_id: str,
        context_type: str,
        context_id: Optional[str]
    ) -> Dict[str, Any]:
        """Get context information for prompts."""
        from app.repositories.course_repository import CourseRepository
        from app.repositories.chapter_repository import ChapterRepository
        from app.repositories.lesson_repository import LessonRepository

        info = {'course': {}, 'chapter': {}, 'lesson': {}}

        try:
            # Get course info
            course = CourseRepository.find_by_id(course_id)
            if course:
                info['course'] = {
                    'course_id': str(course.get('course_id')),
                    'title': course.get('title', ''),
                    'description': course.get('description', ''),
                    'category': course.get('category', '')
                }

            # Get specific context
            if context_type == 'chapter' and context_id:
                chapter = ChapterRepository.find_by_id(context_id)
                if chapter:
                    info['chapter'] = {
                        'chapter_id': str(chapter.get('chapter_id')),
                        'title': chapter.get('title', ''),
                        'description': chapter.get('description', '')
                    }

            elif context_type == 'lesson' and context_id:
                lesson = LessonRepository.find_by_id(context_id)
                if lesson:
                    info['lesson'] = {
                        'lesson_id': str(lesson.get('lesson_id')),
                        'title': lesson.get('title', ''),
                        'lm_type': lesson.get('lm_type', 'LM00')
                    }
                    # Also get chapter info
                    chapter_id = lesson.get('chapter_id')
                    if chapter_id:
                        chapter = ChapterRepository.find_by_id(chapter_id)
                        if chapter:
                            info['chapter'] = {
                                'chapter_id': str(chapter.get('chapter_id')),
                                'title': chapter.get('title', '')
                            }

        except Exception as e:
            logger.warning(f"Error getting context info: {e}")

        return info

    def _format_conversation_history(self, messages: List[Dict]) -> str:
        """Format conversation history for prompt."""
        if not messages:
            return "Keine vorherigen Nachrichten."

        formatted = []
        for msg in messages[-5:]:  # Last 5 messages
            role = "Benutzer" if msg['role'] == 'user' else "Assistent"
            formatted.append(f"{role}: {msg['content'][:200]}...")

        return "\n".join(formatted)

    def _extract_json(self, text: str) -> Optional[Dict]:
        """Extract JSON from text response."""
        # Try to find JSON block
        if '```json' in text:
            start = text.find('```json') + 7
            end = text.find('```', start)
            if end > start:
                return json.loads(text[start:end].strip())

        # Try to parse as JSON directly
        if text.strip().startswith('{'):
            # Find the JSON object
            brace_count = 0
            start = text.find('{')
            for i, char in enumerate(text[start:], start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        return json.loads(text[start:i+1])

        return None

    def _extract_text_before_json(self, text: str) -> str:
        """Extract text before JSON block."""
        if '```json' in text:
            return text[:text.find('```json')].strip()
        if text.strip().startswith('{'):
            return ""
        return text

    # === Preview Methods ===

    def _preview_chapter_theory(self, content: Dict, format_type: str) -> Dict[str, Any]:
        """Generate preview for chapter theory."""
        if format_type == 'html':
            html = ['<div class="chapter-theory-preview">']

            if content.get('overview'):
                html.append(f'<div class="overview"><h3>Übersicht</h3><p>{content["overview"]}</p></div>')

            if content.get('learningGoals'):
                html.append('<div class="learning-goals"><h3>Lernziele</h3><ul>')
                for goal in content['learningGoals']:
                    html.append(f'<li>{goal}</li>')
                html.append('</ul></div>')

            if content.get('concepts'):
                html.append('<div class="concepts"><h3>Konzepte</h3>')
                for concept in content['concepts']:
                    html.append(f'<div class="concept"><h4>{concept.get("emoji", "")} {concept.get("title", "")}</h4>')
                    html.append(f'<p>{concept.get("description", concept.get("oneLiner", ""))}</p>')
                    if concept.get('formula'):
                        html.append(f'<code class="formula">{concept["formula"]}</code>')
                    html.append('</div>')
                html.append('</div>')

            if content.get('terms'):
                html.append('<div class="terms"><h3>Begriffe</h3><dl>')
                for term in content['terms']:
                    html.append(f'<dt>{term.get("term", "")}</dt>')
                    html.append(f'<dd>{term.get("simple", term.get("definition", ""))}</dd>')
                html.append('</dl></div>')

            html.append('</div>')
            return {'preview': '\n'.join(html), 'format': 'html'}
        else:
            return {'preview': json.dumps(content, indent=2, ensure_ascii=False), 'format': 'json'}

    def _preview_lesson_explanation(self, content: Dict, format_type: str) -> Dict[str, Any]:
        """Generate preview for lesson explanation."""
        if format_type == 'html':
            html = ['<div class="lesson-explanation-preview">']

            if content.get('steps'):
                html.append('<div class="steps">')
                for i, step in enumerate(content['steps'], 1):
                    html.append(f'<div class="step"><h4>Schritt {i}: {step.get("title", "")}</h4>')
                    html.append(f'<p class="speech">{step.get("speech", "")}</p>')
                    if step.get('calculator'):
                        html.append(f'<code class="calculator">{step["calculator"]} = {step.get("result", "")}</code>')
                    html.append('</div>')
                html.append('</div>')

            html.append('</div>')
            return {'preview': '\n'.join(html), 'format': 'html'}
        else:
            return {'preview': json.dumps(content, indent=2, ensure_ascii=False), 'format': 'json'}

    def _preview_task(self, content: Dict, format_type: str) -> Dict[str, Any]:
        """Generate preview for task."""
        if format_type == 'html':
            html = ['<div class="task-preview">']

            if content.get('title'):
                html.append(f'<h3>{content["title"]}</h3>')

            if content.get('description'):
                html.append(f'<div class="description">{content["description"]}</div>')

            if content.get('instructions'):
                html.append(f'<div class="instructions"><strong>Aufgabe:</strong> {content["instructions"]}</div>')

            html.append('</div>')
            return {'preview': '\n'.join(html), 'format': 'html'}
        else:
            return {'preview': json.dumps(content, indent=2, ensure_ascii=False), 'format': 'json'}

    def _preview_learning_method(self, content: Dict, format_type: str) -> Dict[str, Any]:
        """Generate preview for learning method."""
        return {'preview': json.dumps(content, indent=2, ensure_ascii=False), 'format': 'json'}

    # === Save Methods ===

    def _save_chapter(self, data: Dict, user_id: str) -> Dict[str, Any]:
        """Save new chapter."""
        from app.repositories.chapter_repository import ChapterRepository

        chapter_data = {
            'course_id': data.get('course_id'),
            'title': data.get('title'),
            'description': data.get('description'),
            'duration_minutes': data.get('duration_minutes', 0)
        }

        chapter = ChapterRepository.create(chapter_data)
        logger.info(f"Created chapter: {chapter.get('chapter_id')}")

        return {
            'success': True,
            'content_type': 'chapter',
            'chapter_id': str(chapter.get('chapter_id')),
            'title': chapter.get('title')
        }

    def _save_chapter_theory(self, data: Dict, user_id: str) -> Dict[str, Any]:
        """Save chapter theory."""
        from app.database.connection import fetch_one

        query = """
            INSERT INTO chapter_theory (
                chapter_id, style, title, theory_data,
                tokens_used, model_used, generated_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING theory_id, chapter_id, title, created_at
        """

        result = fetch_one(query, (
            data.get('chapter_id'),
            data.get('style', 'standard'),
            data.get('title', 'Generierte Theorie'),
            json.dumps(data.get('theory_data', {})),
            data.get('tokens_used', 0),
            data.get('model_used', 'unknown'),
            user_id
        ))

        logger.info(f"Created chapter theory: {result.get('theory_id')}")

        return {
            'success': True,
            'content_type': 'chapter_theory',
            'theory_id': str(result.get('theory_id')),
            'chapter_id': str(result.get('chapter_id'))
        }

    def _save_lesson(self, data: Dict, user_id: str) -> Dict[str, Any]:
        """Save new lesson."""
        from app.repositories.lesson_repository import LessonRepository

        lesson_data = {
            'chapter_id': data.get('chapter_id'),
            'title': data.get('title'),
            'lesson_type': data.get('lesson_type', 'text'),
            'content': json.dumps(data.get('content', {})),
            'duration_minutes': data.get('duration_minutes', 10)
        }

        lesson = LessonRepository.create(lesson_data)
        logger.info(f"Created lesson: {lesson.get('lesson_id')}")

        return {
            'success': True,
            'content_type': 'lesson',
            'lesson_id': str(lesson.get('lesson_id')),
            'title': lesson.get('title')
        }

    def _save_lesson_explanation(self, data: Dict, user_id: str) -> Dict[str, Any]:
        """Save lesson explanation."""
        from app.database.connection import fetch_one

        query = """
            INSERT INTO lesson_explanations (
                lesson_id, style, title, explanation_data,
                tokens_used, model_used, generated_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING explanation_id, lesson_id, title, created_at
        """

        result = fetch_one(query, (
            data.get('lesson_id'),
            data.get('style', 'standard'),
            data.get('title', 'Generierte Erklärung'),
            json.dumps(data.get('explanation_data', {})),
            data.get('tokens_used', 0),
            data.get('model_used', 'unknown'),
            user_id
        ))

        logger.info(f"Created lesson explanation: {result.get('explanation_id')}")

        return {
            'success': True,
            'content_type': 'lesson_explanation',
            'explanation_id': str(result.get('explanation_id')),
            'lesson_id': str(result.get('lesson_id'))
        }

    def _save_task(self, data: Dict, user_id: str) -> Dict[str, Any]:
        """Save new task/exercise."""
        # Tasks are typically stored as learning method instances
        return self._save_learning_method({
            **data,
            'method_type': data.get('method_type', 8)  # LM08 = Whiteboard Tasks
        }, user_id)

    def _save_learning_method(self, data: Dict, user_id: str) -> Dict[str, Any]:
        """Save learning method instance."""
        from app.repositories.learning_method_instance_repository import LearningMethodInstanceRepository

        method_data = {
            'chapter_id': data.get('chapter_id'),
            'lesson_id': data.get('lesson_id'),
            'method_type': data.get('method_type', 0),
            'title': data.get('title'),
            'instructions': data.get('instructions'),
            'data': data.get('data', {}),
            'solution': data.get('solution'),
            'difficulty': data.get('difficulty', 'medium'),
            'tier': data.get('tier', 'basic')
        }

        method = LearningMethodInstanceRepository.create(method_data)
        logger.info(f"Created learning method: {method.get('method_id')}")

        return {
            'success': True,
            'content_type': 'learning_method',
            'method_id': str(method.get('method_id')),
            'method_type': method.get('method_type')
        }


# Convenience function
def get_authoring_service(
    provider: str = "anthropic",
    model: str = "claude-3-5-sonnet-20241022"
) -> AuthoringService:
    """Get authoring service instance."""
    return AuthoringService(provider=provider, model=model)
