"""
LernsystemX Learning Method Repository

Data access layer for AI-powered learning methods:
- CRUD operations for learning methods
- AI execution with token tracking
- User token balance management
- Feedback collection and analytics
- Usage statistics

Uses:
- Pure psycopg for PostgreSQL access
- AIAdapter for multi-provider AI integration
- Connection pooling for performance

ISO 27001:2013 compliant - AI execution and data privacy
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import psycopg
from psycopg.rows import dict_row

from app.extensions import db_pool
from app.services.ai_adapter import AIAdapter, AIProviderError, AITimeoutError, AIQuotaExceededError
from app.services.cache_service import CacheService
from flask import current_app


class LearningMethodRepository:
    """
    Learning Method Repository with AI integration

    All methods use psycopg connection pool and return dictionaries.
    """

    @classmethod
    def get_all(cls, active_only: bool = False, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Get all learning methods

        Args:
            active_only: Only return active methods
            use_cache: Use cache (default: True)

        Returns:
            List of learning method dictionaries
        """
        # Try cache first
        if use_cache:
            cache_suffix = 'active' if active_only else 'all'
            cache_key = CacheService.make_key('METHODS', 'list', cache_suffix)
            ttl = current_app.config.get('CACHE_LEARNING_METHOD_TTL', 3600)

            def load_methods():
                with db_pool.connection() as conn:
                    with conn.cursor(row_factory=dict_row) as cur:
                        # Actual table uses: method_id (UUID), method_type (int 0-31), title, tier, data (jsonb)
                        query = """
                            SELECT
                                lm.method_id,
                                lm.method_type,
                                lm.title as name,
                                lm.instructions as description,
                                lm.tier,
                                lm.data as config,
                                lm.published as active,
                                lm.created_at,
                                lm.updated_at,
                                0 as usage_count
                            FROM learning_methods lm
                        """

                        if active_only:
                            query += " WHERE lm.published = TRUE"

                        query += """
                            ORDER BY lm.tier, lm.title
                        """

                        cur.execute(query)
                        return cur.fetchall()

            return CacheService.cache_get_or_set(cache_key, ttl, load_methods)

        # Bypass cache
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Actual table uses: method_id (UUID), method_type (int 0-31), title, tier, data (jsonb)
                query = """
                    SELECT
                        lm.method_id,
                        lm.method_type,
                        lm.title as name,
                        lm.instructions as description,
                        lm.tier,
                        lm.data as config,
                        lm.published as active,
                        lm.created_at,
                        lm.updated_at,
                        0 as usage_count
                    FROM learning_methods lm
                """

                if active_only:
                    query += " WHERE lm.published = TRUE"

                query += """
                    ORDER BY lm.tier, lm.title
                """

                cur.execute(query)
                return cur.fetchall()

    @classmethod
    def find_by_id(cls, method_id: str) -> Optional[Dict[str, Any]]:
        """
        Find learning method by ID

        Args:
            method_id: Learning method UUID

        Returns:
            Learning method dictionary or None
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT
                        lm.method_id,
                        lm.method_type,
                        lm.title as name,
                        lm.instructions as description,
                        lm.tier,
                        lm.data as config,
                        lm.published as active,
                        lm.created_at,
                        lm.updated_at,
                        0 as usage_count
                    FROM learning_methods lm
                    WHERE lm.method_id = %s
                """, (method_id,))

                return cur.fetchone()

    @classmethod
    def find_by_name(cls, name: str) -> Optional[Dict[str, Any]]:
        """
        Find learning method by name (title)

        Args:
            name: Learning method title

        Returns:
            Learning method dictionary or None
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT
                        method_id,
                        method_type,
                        title as name,
                        instructions as description,
                        tier,
                        data as config,
                        published as active,
                        created_at,
                        updated_at
                    FROM learning_methods
                    WHERE title = %s
                """, (name,))

                return cur.fetchone()

    @classmethod
    def create(cls, method_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new learning method

        Args:
            method_data: Learning method data

        Returns:
            Created learning method dictionary
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    INSERT INTO learning_methods (
                        name, description, tier, config, active
                    ) VALUES (%s, %s, %s, %s, %s)
                    RETURNING *
                """, (
                    method_data['name'],
                    method_data.get('description'),
                    method_data['tier'],
                    psycopg.types.json.Jsonb(method_data.get('config', {})),
                    method_data.get('active', True)
                ))

                conn.commit()
                result = cur.fetchone()

                # Invalidate learning methods cache after creation
                if result:
                    CacheService.invalidate_learning_methods_cache()

                return result

    @classmethod
    def update(cls, method_id: str, method_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update learning method

        Args:
            method_id: Learning method ID
            method_data: Updated data

        Returns:
            Updated learning method or None
        """
        # Build dynamic update query
        update_fields = []
        params = []

        for key, value in method_data.items():
            if key == 'config':
                update_fields.append(f"{key} = %s")
                params.append(psycopg.types.json.Jsonb(value))
            else:
                update_fields.append(f"{key} = %s")
                params.append(value)

        if not update_fields:
            return cls.find_by_id(method_id)

        params.append(method_id)

        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                query = f"""
                    UPDATE learning_methods
                    SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                    WHERE method_id = %s
                    RETURNING *
                """

                cur.execute(query, params)
                conn.commit()
                result = cur.fetchone()

                # Invalidate learning methods cache after update
                if result:
                    CacheService.invalidate_learning_methods_cache()

                return result

    @classmethod
    def delete(cls, method_id: str) -> bool:
        """
        Delete learning method (hard delete)

        Args:
            method_id: Learning method ID

        Returns:
            True if deleted, False if not found
        """
        with db_pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM learning_methods
                    WHERE method_id = %s
                """, (method_id,))

                conn.commit()
                deleted = cur.rowcount > 0

                # Invalidate learning methods cache after deletion
                if deleted:
                    CacheService.invalidate_learning_methods_cache()

                return deleted

    @classmethod
    def activate(cls, method_id: str) -> Optional[Dict[str, Any]]:
        """Activate learning method"""
        return cls.update(method_id, {'active': True})

    @classmethod
    def deactivate(cls, method_id: str) -> Optional[Dict[str, Any]]:
        """Deactivate learning method"""
        return cls.update(method_id, {'active': False})

    # ========================================================================
    # AI EXECUTION METHODS
    # ========================================================================

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
        Execute AI-powered learning method

        Args:
            user_id: User ID
            method_id: Learning method ID
            user_input: User's question/input
            context: Additional context
            language: Response language
            difficulty: Difficulty level
            conversation_history: Previous conversation turns
            course_id: Course ID (optional context)
            chapter_id: Chapter ID (optional context)
            lesson_id: Lesson ID (optional context)

        Returns:
            {
                'execution_id': int,
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
        method = cls.find_by_id(method_id)

        if not method:
            raise ValueError(f'Learning method {method_id} not found')

        if not method['active']:
            raise ValueError(f'Learning method "{method["name"]}" is not active')

        # Get AI configuration from method config
        config = method.get('config', {})
        ai_model = config.get('ai_model', 'gpt-4o-mini')
        provider = config.get('ai_provider', 'openai')

        # Build the prompt using method instructions and lesson content
        method_name = method.get('name', 'Lernmethode')
        method_description = method.get('description', '')
        method_type = method.get('method_type')  # LM-ID (e.g., 12 for Mathe-Interaktiv)

        # Fetch lesson content if lesson_id is provided
        lesson_content = None
        lesson_title = None
        course_title = None
        if lesson_id:
            try:
                with db_pool.connection() as conn:
                    with conn.cursor(row_factory=dict_row) as cur:
                        # Get lesson with course and chapter info
                        cur.execute("""
                            SELECT
                                l.title as lesson_title,
                                l.content as lesson_content,
                                l.description as lesson_description,
                                c.title as course_title,
                                ch.title as chapter_title
                            FROM lessons l
                            LEFT JOIN chapters ch ON l.chapter_id = ch.chapter_id
                            LEFT JOIN courses c ON ch.course_id = c.course_id
                            WHERE l.lesson_id = %s
                        """, (lesson_id,))
                        lesson_data = cur.fetchone()
                        if lesson_data:
                            lesson_title = lesson_data.get('lesson_title', '')
                            lesson_content = lesson_data.get('lesson_content', {})
                            course_title = lesson_data.get('course_title', '')
            except Exception as e:
                current_app.logger.warning(f'Failed to fetch lesson content: {e}')

        # Build the actual prompt based on method type
        # If user_input is empty, construct a task generation prompt
        if not user_input or user_input.strip() == '':
            # Generate task prompt based on method description and lesson content
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

        # Initialize AI Adapter
        try:
            adapter = AIAdapter(provider=provider, model=ai_model)
        except Exception as e:
            raise AIProviderError(f'Failed to initialize AI adapter: {str(e)}')

        # Send AI request
        try:
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
        with db_pool.connection() as conn:
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
                    user_input, ai_response['output_text'], context, language, difficulty,
                    ai_response['input_tokens'], ai_response['output_tokens'], ai_response['total_tokens'],
                    ai_response['model'], ai_response['provider'], ai_response['latency_ms'], ai_response['cost_eur']
                ))

                execution = cur.fetchone()
                conn.commit()

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
        Build a proper prompt for the learning method based on its type and lesson content.

        Args:
            method_type: Learning method type ID (LM-ID like 12 for Mathe-Interaktiv)
            method_name: Name of the learning method
            method_description: Description/instructions for the method
            lesson_title: Title of the lesson
            lesson_content: Content of the lesson (JSONB)
            course_title: Title of the course
            difficulty: Difficulty level
            language: Target language

        Returns:
            Constructed prompt string for the AI
        """
        import json

        # Extract text content from lesson_content if it's a dict/JSON
        content_text = ''
        if lesson_content:
            if isinstance(lesson_content, dict):
                # Try to extract text from common content structures
                content_text = lesson_content.get('text', '')
                if not content_text:
                    content_text = lesson_content.get('content', '')
                if not content_text:
                    content_text = lesson_content.get('body', '')
                if not content_text:
                    # Fallback: convert entire JSON to string
                    content_text = json.dumps(lesson_content, ensure_ascii=False, indent=2)
            elif isinstance(lesson_content, str):
                content_text = lesson_content

        # Build context parts
        context_parts = []
        if course_title:
            context_parts.append(f"Kurs: {course_title}")
        if lesson_title:
            context_parts.append(f"Lektion: {lesson_title}")
        context_str = ", ".join(context_parts) if context_parts else "Allgemeiner Kontext"

        difficulty_str = difficulty or "mittel"

        # Method-specific prompt templates based on method_type (LM-ID)
        # LM12 = Mathe-Interaktiv
        if method_type == 12:
            prompt = f"""Du bist ein KI-Tutor für Mathematik und Kalkulationen im Bereich IHK-Prüfungsvorbereitung.

Kontext: {context_str}
Schwierigkeitsgrad: {difficulty_str}

Aufgabe: {method_description}

Basierend auf dem Lektionsinhalt, erstelle eine interaktive Mathematik-Aufgabe.

Lektionsinhalt:
{content_text[:2000] if content_text else 'Bezugskalkulation und kaufmännisches Rechnen'}

Erstelle eine Rechenaufgabe mit:
1. Einer klaren Aufgabenstellung
2. Realistischen Zahlen (z.B. Einkaufspreise, Rabatte, Bezugskosten)
3. Schritt-für-Schritt Lösung zum Aufklappen
4. Erklärung des Rechenwegs

Format die Ausgabe als strukturierte Aufgabe mit Lösung."""

        # LM0 = Deep Explanation
        elif method_type == 0:
            prompt = f"""Du bist ein erfahrener KI-Tutor.

Kontext: {context_str}
Aufgabe: {method_description}

Erkläre das Thema "{lesson_title or 'dieses Konzept'}" tiefgehend mit:
1. Einer klaren Definition
2. Praktischen Beispielen
3. Analogien zum besseren Verständnis
4. Zusammenfassung der Kernpunkte

Lektionsinhalt zur Referenz:
{content_text[:2000] if content_text else 'Keine spezifischen Inhalte verfügbar'}"""

        # LM1 = Step-by-Step
        elif method_type == 1:
            prompt = f"""Du bist ein KI-Tutor für schrittweise Erklärungen.

Kontext: {context_str}
Aufgabe: {method_description}

Erkläre das Thema "{lesson_title or 'dieses Konzept'}" in nummerierten Schritten:
1. Beginne mit den Grundlagen
2. Baue systematisch darauf auf
3. Verwende praktische Beispiele
4. Schließe mit einer Zusammenfassung ab

Lektionsinhalt:
{content_text[:2000] if content_text else 'Keine spezifischen Inhalte verfügbar'}"""

        # LM13 = Flashcards
        elif method_type == 13:
            prompt = f"""Erstelle Lernkarten (Flashcards) für das Thema.

Kontext: {context_str}
Aufgabe: {method_description}

Basierend auf dem Lektionsinhalt, erstelle 5-10 Flashcards im Format:
**Frage:** [Frage hier]
**Antwort:** [Antwort hier]
---

Lektionsinhalt:
{content_text[:2000] if content_text else 'Keine spezifischen Inhalte verfügbar'}"""

        # LM19 = IHK-Style Tasks
        elif method_type == 19:
            prompt = f"""Du bist ein IHK-Prüfungsexperte.

Kontext: {context_str}
Schwierigkeitsgrad: {difficulty_str}
Aufgabe: {method_description}

Erstelle eine prüfungsnahe Aufgabe im IHK-Stil mit:
1. Situationsbeschreibung
2. Konkrete Fragestellung
3. Relevante Daten/Zahlen
4. Musterlösung mit Punkteverteilung

Lektionsinhalt:
{content_text[:2000] if content_text else 'Kaufmännische Inhalte'}"""

        # LM22 = Exam Quiz
        elif method_type == 22:
            prompt = f"""Erstelle ein Quiz zum Thema.

Kontext: {context_str}
Aufgabe: {method_description}

Erstelle 5 Multiple-Choice-Fragen mit:
- 4 Antwortmöglichkeiten pro Frage
- Einer korrekten Antwort (markiert)
- Kurzer Erklärung warum die Antwort richtig ist

Lektionsinhalt:
{content_text[:2000] if content_text else 'Keine spezifischen Inhalte verfügbar'}"""

        # Default prompt for other method types
        else:
            prompt = f"""Du bist ein KI-Tutor für die Lernmethode "{method_name}".

Kontext: {context_str}
Schwierigkeitsgrad: {difficulty_str}

Aufgabe: {method_description if method_description else 'Erstelle eine interaktive Lernaufgabe zum Thema.'}

Thema der Lektion: {lesson_title or 'Allgemeines Thema'}

Lektionsinhalt:
{content_text[:2000] if content_text else 'Erstelle eine passende Aufgabe basierend auf dem Lektionsthema.'}

Erstelle eine strukturierte, interaktive Aufgabe die dem Lernenden hilft, das Thema zu verstehen und zu üben."""

        return prompt

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
        organization_id: Optional[str] = None,
        course_id: Optional[str] = None,
        chapter_id: Optional[str] = None,
        lesson_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log AI token usage

        Args:
            user_id: User ID
            method_id: Learning method ID
            method_name: Method name
            input_tokens: Input tokens
            output_tokens: Output tokens
            model: AI model
            provider: AI provider
            cost_eur: Cost in EUR
            organization_id: Organization ID (optional)
            course_id: Course ID (optional)
            chapter_id: Chapter ID (optional)
            lesson_id: Lesson ID (optional)

        Returns:
            Token usage record
        """
        total_tokens = input_tokens + output_tokens

        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    INSERT INTO ai_token_usage (
                        user_id, organization_id, method_id, method_name,
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
                    user_id, organization_id, method_id, method_name,
                    course_id, chapter_id, lesson_id,
                    input_tokens, output_tokens, total_tokens,
                    model, provider, cost_eur
                ))

                conn.commit()
                return cur.fetchone()

    @classmethod
    def get_user_token_usage(
        cls,
        user_id: str,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get user's token usage statistics

        Args:
            user_id: User ID
            period_days: Period in days (default 30)

        Returns:
            {
                'total_tokens': int,
                'total_cost_eur': float,
                'total_requests': int,
                'by_method': dict,
                'by_provider': dict,
                'by_model': dict
            }
        """
        period_start = datetime.now() - timedelta(days=period_days)

        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Total stats
                cur.execute("""
                    SELECT
                        COALESCE(SUM(total_tokens), 0) as total_tokens,
                        COALESCE(SUM(cost_eur), 0) as total_cost_eur,
                        COUNT(*) as total_requests
                    FROM ai_token_usage
                    WHERE user_id = %s AND used_at >= %s
                """, (user_id, period_start))

                totals = cur.fetchone()

                # By method
                cur.execute("""
                    SELECT
                        method_name,
                        SUM(total_tokens) as tokens
                    FROM ai_token_usage
                    WHERE user_id = %s AND used_at >= %s
                    GROUP BY method_name
                """, (user_id, period_start))

                by_method = {row['method_name']: row['tokens'] for row in cur.fetchall()}

                # By provider
                cur.execute("""
                    SELECT
                        provider,
                        SUM(total_tokens) as tokens
                    FROM ai_token_usage
                    WHERE user_id = %s AND used_at >= %s
                    GROUP BY provider
                """, (user_id, period_start))

                by_provider = {row['provider']: row['tokens'] for row in cur.fetchall()}

                # By model
                cur.execute("""
                    SELECT
                        model,
                        SUM(total_tokens) as tokens
                    FROM ai_token_usage
                    WHERE user_id = %s AND used_at >= %s
                    GROUP BY model
                """, (user_id, period_start))

                by_model = {row['model']: row['tokens'] for row in cur.fetchall()}

                return {
                    'user_id': user_id,
                    'total_tokens': totals['total_tokens'],
                    'total_cost_eur': float(totals['total_cost_eur']),
                    'total_requests': totals['total_requests'],
                    'by_method': by_method,
                    'by_provider': by_provider,
                    'by_model': by_model,
                    'period_start': period_start,
                    'period_end': datetime.now()
                }

    # ========================================================================
    # FEEDBACK METHODS
    # ========================================================================

    @classmethod
    def create_feedback(
        cls,
        user_id: str,
        execution_id: str,
        rating: int,
        feedback_text: Optional[str] = None,
        is_helpful: bool = True,
        ai_generated: bool = False,
        course_id: Optional[str] = None,
        chapter_id: Optional[str] = None,
        lesson_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create AI feedback

        Args:
            user_id: User ID
            execution_id: Execution ID
            rating: Rating (1-5)
            feedback_text: Feedback text
            is_helpful: Was response helpful
            ai_generated: Is feedback AI-generated
            course_id: Course ID (optional)
            chapter_id: Chapter ID (optional)
            lesson_id: Lesson ID (optional)

        Returns:
            Feedback record
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Get method_id from execution
                cur.execute("""
                    SELECT method_id FROM learning_method_executions
                    WHERE execution_id = %s
                """, (execution_id,))

                execution = cur.fetchone()
                if not execution:
                    raise ValueError(f'Execution {execution_id} not found')

                method_id = execution['method_id']

                # Create feedback
                cur.execute("""
                    INSERT INTO ai_feedback (
                        user_id, execution_id, method_id,
                        course_id, chapter_id, lesson_id,
                        rating, feedback_text, is_helpful, ai_generated
                    ) VALUES (
                        %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s, %s
                    )
                    RETURNING *
                """, (
                    user_id, execution_id, method_id,
                    course_id, chapter_id, lesson_id,
                    rating, feedback_text, is_helpful, ai_generated
                ))

                conn.commit()
                return cur.fetchone()

    @classmethod
    def get_method_feedback(cls, method_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get feedback for learning method

        Args:
            method_id: Learning method ID
            limit: Maximum results

        Returns:
            List of feedback records
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT
                        f.*,
                        u.username,
                        u.firstname,
                        u.lastname
                    FROM ai_feedback f
                    JOIN users u ON f.user_id = u.user_id
                    WHERE f.method_id = %s
                    ORDER BY f.created_at DESC
                    LIMIT %s
                """, (method_id, limit))

                return cur.fetchall()

    @classmethod
    def get_feedback_stats(cls, method_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get feedback statistics

        Args:
            method_id: Learning method ID (optional, None for all methods)

        Returns:
            {
                'total_feedback': int,
                'average_rating': float,
                'helpful_count': int,
                'not_helpful_count': int,
                'rating_distribution': {1: count, 2: count, ...}
            }
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Base query
                where_clause = "WHERE method_id = %s" if method_id else ""
                params = (method_id,) if method_id else ()

                # Total stats
                cur.execute(f"""
                    SELECT
                        COUNT(*) as total_feedback,
                        COALESCE(AVG(rating), 0) as average_rating,
                        SUM(CASE WHEN is_helpful = TRUE THEN 1 ELSE 0 END) as helpful_count,
                        SUM(CASE WHEN is_helpful = FALSE THEN 1 ELSE 0 END) as not_helpful_count
                    FROM ai_feedback
                    {where_clause}
                """, params)

                totals = cur.fetchone()

                # Rating distribution
                cur.execute(f"""
                    SELECT
                        rating,
                        COUNT(*) as count
                    FROM ai_feedback
                    {where_clause}
                    GROUP BY rating
                    ORDER BY rating
                """, params)

                rating_dist = {row['rating']: row['count'] for row in cur.fetchall()}

                # Fill in missing ratings with 0
                for rating in range(1, 6):
                    if rating not in rating_dist:
                        rating_dist[rating] = 0

                return {
                    'method_id': method_id,
                    'total_feedback': totals['total_feedback'],
                    'average_rating': float(totals['average_rating']),
                    'helpful_count': totals['helpful_count'],
                    'not_helpful_count': totals['not_helpful_count'],
                    'rating_distribution': rating_dist
                }

    @classmethod
    def get_lesson_executions(
        cls,
        user_id: str,
        lesson_id: str,
        method_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get saved task executions for a lesson

        Args:
            user_id: User ID
            lesson_id: Lesson ID
            method_id: Optional filter by method ID
            limit: Maximum results

        Returns:
            List of execution records with their responses
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                if method_id:
                    cur.execute("""
                        SELECT
                            e.execution_id,
                            e.method_id,
                            e.user_input,
                            e.output_text as ai_response,
                            e.input_tokens,
                            e.output_tokens,
                            e.total_tokens,
                            e.model,
                            e.provider,
                            e.executed_at,
                            m.title as method_name,
                            m.instructions as method_description
                        FROM learning_method_executions e
                        JOIN learning_methods m ON e.method_id = m.method_id
                        WHERE e.user_id = %s
                          AND e.lesson_id = %s
                          AND e.method_id = %s
                        ORDER BY e.executed_at DESC
                        LIMIT %s
                    """, (user_id, lesson_id, method_id, limit))
                else:
                    cur.execute("""
                        SELECT
                            e.execution_id,
                            e.method_id,
                            e.user_input,
                            e.output_text as ai_response,
                            e.input_tokens,
                            e.output_tokens,
                            e.total_tokens,
                            e.model,
                            e.provider,
                            e.executed_at,
                            m.title as method_name,
                            m.instructions as method_description
                        FROM learning_method_executions e
                        JOIN learning_methods m ON e.method_id = m.method_id
                        WHERE e.user_id = %s
                          AND e.lesson_id = %s
                        ORDER BY e.executed_at DESC
                        LIMIT %s
                    """, (user_id, lesson_id, limit))

                executions = cur.fetchall()

                # Convert UUIDs and timestamps to strings for JSON serialization
                for exec_record in executions:
                    exec_record['execution_id'] = str(exec_record['execution_id'])
                    exec_record['method_id'] = str(exec_record['method_id'])
                    if exec_record['executed_at']:
                        exec_record['executed_at'] = exec_record['executed_at'].isoformat()

                return executions

    @classmethod
    def delete_execution(cls, execution_id: str, user_id: str) -> bool:
        """
        Delete a task execution (only if owned by user)

        Args:
            execution_id: Execution UUID
            user_id: User UUID (must be owner)

        Returns:
            True if deleted, False if not found or not owned
        """
        with db_pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM learning_method_executions
                    WHERE execution_id = %s AND user_id = %s
                    RETURNING execution_id
                """, (execution_id, user_id))
                result = cur.fetchone()
                conn.commit()
                return result is not None

    @classmethod
    def get_statistics(cls) -> Dict[str, Any]:
        """
        Get overall learning method statistics

        Returns:
            {
                'total_methods': int,
                'active_methods': int,
                'by_tier': dict,
                'ai_powered_count': int,
                'most_used': str,
                'total_executions': int,
                'total_tokens': int,
                'total_cost_eur': float
            }
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Method counts
                cur.execute("""
                    SELECT
                        COUNT(*) as total_methods,
                        SUM(CASE WHEN active = TRUE THEN 1 ELSE 0 END) as active_methods,
                        SUM(CASE WHEN config->>'ai_enabled' = 'true' THEN 1 ELSE 0 END) as ai_powered_count
                    FROM learning_methods
                """)

                method_stats = cur.fetchone()

                # By tier
                cur.execute("""
                    SELECT tier, COUNT(*) as count
                    FROM learning_methods
                    GROUP BY tier
                """)

                by_tier = {row['tier']: row['count'] for row in cur.fetchall()}

                # Most used method - placeholder since learning_method_usage table doesn't exist
                most_used = None

                # AI execution stats - placeholder since learning_method_executions table doesn't exist
                return {
                    'total_methods': method_stats['total_methods'],
                    'active_methods': method_stats['active_methods'],
                    'by_tier': by_tier,
                    'ai_powered_count': method_stats['ai_powered_count'] or 0,
                    'most_used': most_used,
                    'total_executions': 0,
                    'total_tokens': 0,
                    'total_cost_eur': 0.0
                }
