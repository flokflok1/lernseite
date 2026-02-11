"""
Learning Method Repository - AI Execution

AI-powered method execution with token tracking:
- execute_ai_method: Execute AI-powered learning method
- _build_method_prompt: Generate method-specific prompts
- log_token_usage: Track AI token consumption

Uses AIAdapter for multi-provider integration (Anthropic, OpenAI, etc.)
Token costs tracked in database for billing.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
import psycopg
from psycopg.rows import dict_row

from app.core.bootstrap import extensions
from app.application.services.ai.adapter import AIAdapter, AIProviderError, AITimeoutError, AIQuotaExceededError
from flask import current_app
from .base import LearningMethodBaseRepository


class LearningMethodAIRepository:
    """
    AI execution for learning methods with token tracking and cost analysis.
    """

    @classmethod
    def execute_ai_method(
        cls,
        user_id: str,
        method_id: str,
        user_input: str,
        context: Optional[str] = None,
        language: str = 'de',
        difficulty: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        course_id: Optional[str] = None,
        chapter_id: Optional[str] = None,
        lesson_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute AI-powered learning method with token tracking.

        Args:
            user_id: User ID
            method_id: Learning method ID
            user_input: User's question/input
            context: Additional context
            language: Response language (de, en, etc.)
            difficulty: Difficulty level
            conversation_history: Previous conversation turns
            course_id: Course ID (optional context)
            chapter_id: Chapter ID (optional context)
            lesson_id: Lesson ID (optional context)

        Returns:
            {
                'execution_id': str,
                'method_id': str,
                'method_name': str,
                'output_text': str,
                'input_tokens': int,
                'output_tokens': int,
                'total_tokens': int,
                'model': str,
                'provider': str,
                'latency_ms': int,
                'cost_eur': float,
                'executed_at': datetime
            }

        Raises:
            ValueError: If method not found or not active
            AIProviderError: On AI provider errors
        """
        # Get learning method
        method = LearningMethodBaseRepository.find_by_id(method_id)

        if not method:
            raise ValueError(f'Learning method {method_id} not found')

        if not method['active']:
            raise ValueError(f'Learning method "{method["name"]}" is not active')

        # Get AI configuration from method config
        config = method.get('config', {})
        ai_model = config.get('ai_model', 'gpt-4o-mini')
        provider = config.get('ai_provider', 'openai')

        # Fetch lesson content if provided
        lesson_title, lesson_content, course_title = cls._fetch_lesson_context(lesson_id)
        method_name = method.get('name', 'Lernmethode')
        method_description = method.get('description', '')
        method_type = method.get('method_type')

        # Build the prompt
        if not user_input or user_input.strip() == '':
            prompt = cls._build_method_prompt(
                method_type=method_type,
                method_name=method_name,
                method_description=method_description,
                lesson_title=lesson_title,
                lesson_content=lesson_content,
                course_title=course_title,
                difficulty=difficulty,
                language=language
            )
        else:
            prompt = user_input

        # Enhance context with lesson information
        enhanced_context = context or ''
        if lesson_title and not context:
            enhanced_context = f"Lektion: {lesson_title}"
            if course_title:
                enhanced_context = f"Kurs: {course_title}, {enhanced_context}"

        # Execute AI request
        try:
            adapter = AIAdapter(provider=provider, model=ai_model)
            ai_response = adapter.send_request(
                prompt=prompt,
                context=enhanced_context,
                language=language,
                temperature=config.get('temperature', 0.7),
                max_tokens=config.get('max_tokens', 2000),
                conversation_history=conversation_history
            )
        except AITimeoutError:
            raise AIProviderError('AI request timed out. Please try again.')
        except AIQuotaExceededError:
            raise AIProviderError('AI quota exceeded. Please contact support.')
        except Exception as e:
            raise AIProviderError(f'AI request failed: {str(e)}')

        # Log execution to database
        execution = cls._log_execution(
            user_id=user_id,
            method_id=method_id,
            course_id=course_id,
            chapter_id=chapter_id,
            lesson_id=lesson_id,
            user_input=user_input,
            output_text=ai_response['output_text'],
            context=context,
            language=language,
            difficulty=difficulty,
            ai_response=ai_response
        )

        # Log token usage
        cls.log_token_usage(
            user_id=user_id,
            method_id=method_id,
            method_name=method['name'],
            input_tokens=ai_response['input_tokens'],
            output_tokens=ai_response['output_tokens'],
            model=ai_response['model'],
            provider=ai_response['provider'],
            cost_eur=ai_response['cost_eur'],
            course_id=course_id,
            chapter_id=chapter_id,
            lesson_id=lesson_id
        )

        return {
            'execution_id': execution['execution_id'],
            'method_id': method_id,
            'method_name': method['name'],
            'output_text': ai_response['output_text'],
            'input_tokens': ai_response['input_tokens'],
            'output_tokens': ai_response['output_tokens'],
            'total_tokens': ai_response['total_tokens'],
            'model': ai_response['model'],
            'provider': ai_response['provider'],
            'latency_ms': ai_response['latency_ms'],
            'cost_eur': ai_response['cost_eur'],
            'executed_at': execution['executed_at']
        }

    @classmethod
    def _fetch_lesson_context(cls, lesson_id: Optional[str]) -> tuple:
        """
        Fetch lesson context (title, content, course title) from database.

        Args:
            lesson_id: Lesson ID (optional)

        Returns:
            (lesson_title, lesson_content, course_title) or (None, None, None)
        """
        if not lesson_id:
            return None, None, None

        try:
            with extensions.db_pool.connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute("""
                        SELECT
                            l.title as lesson_title,
                            l.content as lesson_content,
                            l.description as lesson_description,
                            c.title as course_title,
                            ch.title as chapter_title
                        FROM courses.lessons l
                        LEFT JOIN courses.chapters ch ON l.chapter_id = ch.chapter_id
                        LEFT JOIN courses.courses c ON ch.course_id = c.course_id
                        WHERE l.lesson_id = %s
                    """, (lesson_id,))
                    lesson_data = cur.fetchone()

                    if lesson_data:
                        return (
                            lesson_data.get('lesson_title'),
                            lesson_data.get('lesson_content'),
                            lesson_data.get('course_title')
                        )
        except Exception as e:
            current_app.logger.warning(f'Failed to fetch lesson context: {e}')

        return None, None, None

    @classmethod
    def _log_execution(
        cls,
        user_id: str,
        method_id: str,
        course_id: Optional[str],
        chapter_id: Optional[str],
        lesson_id: Optional[str],
        user_input: str,
        output_text: str,
        context: Optional[str],
        language: str,
        difficulty: Optional[str],
        ai_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Log execution to database."""
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    INSERT INTO learning_method_executions (
                        user_id, method_id, course_id, chapter_id, lesson_id,
                        user_input, output_text, context, language, difficulty,
                        input_tokens, output_tokens, total_tokens,
                        model, provider, latency_ms, cost_eur
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s, %s
                    )
                    RETURNING execution_id, executed_at
                """, (
                    user_id, method_id, course_id, chapter_id, lesson_id,
                    user_input, output_text, context, language, difficulty,
                    ai_response['input_tokens'], ai_response['output_tokens'],
                    ai_response['total_tokens'], ai_response['model'],
                    ai_response['provider'], ai_response['latency_ms'],
                    ai_response['cost_eur']
                ))

                conn.commit()
                return cur.fetchone()

    @classmethod
    def _build_method_prompt(
        cls,
        method_type: Optional[int],
        method_name: str,
        method_description: str,
        lesson_title: Optional[str],
        lesson_content: Optional[Any],
        course_title: Optional[str],
        difficulty: Optional[str],
        language: str = 'de'
    ) -> str:
        """
        Build method-specific prompt based on learning method type.

        Args:
            method_type: Learning method type ID (e.g., 0 for LM0)
            method_name: Name of learning method
            method_description: Instructions for method
            lesson_title: Lesson title
            lesson_content: Lesson content (JSONB)
            course_title: Course title
            difficulty: Difficulty level
            language: Target language

        Returns:
            Constructed prompt string for AI
        """
        # Extract text content from lesson_content
        content_text = cls._extract_content_text(lesson_content)

        # Build context parts
        context_parts = []
        if course_title:
            context_parts.append(f"Kurs: {course_title}")
        if lesson_title:
            context_parts.append(f"Lektion: {lesson_title}")
        context_str = ", ".join(context_parts) if context_parts else "Allgemeiner Kontext"

        difficulty_str = difficulty or "mittel"

        # Method-specific prompts
        if method_type == 12:  # LM12 = Mathe-Interaktiv
            return cls._prompt_math_interactive(
                context_str, difficulty_str, method_description, content_text
            )
        elif method_type == 0:  # LM0 = Deep Explanation
            return cls._prompt_deep_explanation(
                context_str, method_description, lesson_title, content_text
            )
        elif method_type == 1:  # LM1 = Step-by-Step
            return cls._prompt_step_by_step(
                context_str, method_description, lesson_title, content_text
            )
        elif method_type == 13:  # LM13 = Flashcards
            return cls._prompt_flashcards(context_str, method_description, content_text)
        elif method_type == 19:  # LM19 = IHK-Style
            return cls._prompt_ihk_style(
                context_str, difficulty_str, method_description, content_text
            )
        elif method_type == 22:  # LM22 = Exam Quiz
            return cls._prompt_exam_quiz(context_str, method_description, content_text)
        else:
            return cls._prompt_default(
                method_name, context_str, difficulty_str, method_description,
                lesson_title, content_text
            )

    @classmethod
    def _extract_content_text(cls, lesson_content: Optional[Any]) -> str:
        """Extract text from lesson content (dict or string)."""
        if not lesson_content:
            return ''

        if isinstance(lesson_content, dict):
            for key in ('text', 'content', 'body'):
                if key in lesson_content:
                    return lesson_content[key]
            return json.dumps(lesson_content, ensure_ascii=False, indent=2)
        elif isinstance(lesson_content, str):
            return lesson_content

        return ''

    @staticmethod
    def _prompt_math_interactive(context: str, difficulty: str, task: str, content: str) -> str:
        """Prompt for math interactive method (LM12)."""
        return f"""Du bist ein KI-Tutor für Mathematik und Kalkulationen im Bereich IHK-Prüfungsvorbereitung.

Kontext: {context}
Schwierigkeitsgrad: {difficulty}

Aufgabe: {task}

Basierend auf dem Lektionsinhalt, erstelle eine interaktive Mathematik-Aufgabe.

Lektionsinhalt:
{content[:2000] if content else 'Bezugskalkulation und kaufmännisches Rechnen'}

Erstelle eine Rechenaufgabe mit:
1. Einer klaren Aufgabenstellung
2. Realistischen Zahlen (z.B. Einkaufspreise, Rabatte, Bezugskosten)
3. Schritt-für-Schritt Lösung zum Aufklappen
4. Erklärung des Rechenwegs

Format die Ausgabe als strukturierte Aufgabe mit Lösung."""

    @staticmethod
    def _prompt_deep_explanation(context: str, task: str, lesson: str, content: str) -> str:
        """Prompt for deep explanation method (LM0)."""
        return f"""Du bist ein erfahrener KI-Tutor.

Kontext: {context}
Aufgabe: {task}

Erkläre das Thema "{lesson or 'dieses Konzept'}" tiefgehend mit:
1. Einer klaren Definition
2. Praktischen Beispielen
3. Analogien zum besseren Verständnis
4. Zusammenfassung der Kernpunkte

Lektionsinhalt zur Referenz:
{content[:2000] if content else 'Keine spezifischen Inhalte verfügbar'}"""

    @staticmethod
    def _prompt_step_by_step(context: str, task: str, lesson: str, content: str) -> str:
        """Prompt for step-by-step method (LM1)."""
        return f"""Du bist ein KI-Tutor für schrittweise Erklärungen.

Kontext: {context}
Aufgabe: {task}

Erkläre das Thema "{lesson or 'dieses Konzept'}" in nummerierten Schritten:
1. Beginne mit den Grundlagen
2. Baue systematisch darauf auf
3. Verwende praktische Beispiele
4. Schließe mit einer Zusammenfassung ab

Lektionsinhalt:
{content[:2000] if content else 'Keine spezifischen Inhalte verfügbar'}"""

    @staticmethod
    def _prompt_flashcards(context: str, task: str, content: str) -> str:
        """Prompt for flashcards method (LM13)."""
        return f"""Erstelle Lernkarten (Flashcards) für das Thema.

Kontext: {context}
Aufgabe: {task}

Basierend auf dem Lektionsinhalt, erstelle 5-10 Flashcards im Format:
**Frage:** [Frage hier]
**Antwort:** [Antwort hier]
---

Lektionsinhalt:
{content[:2000] if content else 'Keine spezifischen Inhalte verfügbar'}"""

    @staticmethod
    def _prompt_ihk_style(context: str, difficulty: str, task: str, content: str) -> str:
        """Prompt for IHK-style method (LM19)."""
        return f"""Du bist ein IHK-Prüfungsexperte.

Kontext: {context}
Schwierigkeitsgrad: {difficulty}
Aufgabe: {task}

Erstelle eine prüfungsnahe Aufgabe im IHK-Stil mit:
1. Situationsbeschreibung
2. Konkrete Fragestellung
3. Relevante Daten/Zahlen
4. Musterlösung mit Punkteverteilung

Lektionsinhalt:
{content[:2000] if content else 'Kaufmännische Inhalte'}"""

    @staticmethod
    def _prompt_exam_quiz(context: str, task: str, content: str) -> str:
        """Prompt for exam quiz method (LM22)."""
        return f"""Erstelle ein Quiz zum Thema.

Kontext: {context}
Aufgabe: {task}

Erstelle 5 Multiple-Choice-Fragen mit:
- 4 Antwortmöglichkeiten pro Frage
- Einer korrekten Antwort (markiert)
- Kurzer Erklärung warum die Antwort richtig ist

Lektionsinhalt:
{content[:2000] if content else 'Keine spezifischen Inhalte verfügbar'}"""

    @staticmethod
    def _prompt_default(name: str, context: str, difficulty: str, task: str,
                       lesson: str, content: str) -> str:
        """Default prompt for unknown method types."""
        return f"""Du bist ein KI-Tutor für die Lernmethode "{name}".

Kontext: {context}
Schwierigkeitsgrad: {difficulty}

Aufgabe: {task if task else 'Erstelle eine interaktive Lernaufgabe zum Thema.'}

Thema der Lektion: {lesson or 'Allgemeines Thema'}

Lektionsinhalt:
{content[:2000] if content else 'Erstelle eine passende Aufgabe basierend auf dem Lektionsthema.'}

Erstelle eine strukturierte, interaktive Aufgabe die dem Lernenden hilft, das Thema zu verstehen und zu üben."""

    @classmethod
    def log_token_usage(
        cls,
        user_id: str,
        method_id: str,
        method_name: str,
        input_tokens: int,
        output_tokens: int,
        model: str,
        provider: str,
        cost_eur: float,
        organisation_id: Optional[str] = None,
        course_id: Optional[str] = None,
        chapter_id: Optional[str] = None,
        lesson_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log AI token usage to database.

        Args:
            user_id: User ID
            method_id: Learning method ID
            method_name: Method name
            input_tokens: Input tokens used
            output_tokens: Output tokens generated
            model: AI model name
            provider: AI provider (anthropic, openai, etc.)
            cost_eur: Cost in EUR
            organisation_id: Organization ID (optional)
            course_id: Course ID (optional)
            chapter_id: Chapter ID (optional)
            lesson_id: Lesson ID (optional)

        Returns:
            Token usage record
        """
        total_tokens = input_tokens + output_tokens

        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    INSERT INTO ai_token_usage (
                        user_id, organisation_id, method_id, method_name,
                        course_id, chapter_id, lesson_id,
                        input_tokens, output_tokens, total_tokens,
                        model, provider, cost_eur
                    ) VALUES (
                        %s, %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s
                    )
                    RETURNING *
                """, (
                    user_id, organisation_id, method_id, method_name,
                    course_id, chapter_id, lesson_id,
                    input_tokens, output_tokens, total_tokens,
                    model, provider, cost_eur
                ))

                conn.commit()
                return cur.fetchone()
