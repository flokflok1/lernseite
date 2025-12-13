"""
LernsystemX AI Studio Repository

Data access layer for KI-Authoring-Studio:
- CRUD operations for authoring sessions
- Session snapshots (undo/redo)
- Generation variants
- Templates
- Analytics events
- PDF cache

Phase D4 - KI-Authoring-Studio - ISO 27001:2013 compliant
"""

from typing import Optional, Dict, List, Any
from datetime import datetime
import json
import hashlib

from app.database.connection import fetch_one, fetch_all, execute_query, insert_returning, update_returning


class AIStudioRepository:
    """
    Repository for AI Authoring Studio sessions
    """

    table_name = 'ai_authoring_sessions'

    @classmethod
    def create_session(cls, session_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new authoring session

        Args:
            session_data: Session data including:
                - user_id: UUID (required)
                - course_id: UUID (required)
                - session_name: str (optional)
                - source_type: str (optional, default 'manual')
                - ai_config: dict (optional)

        Returns:
            Created session with session_id
        """
        defaults = {
            'status': 'draft',
            'source_type': 'manual',
            'source_data': '{}',
            'ai_config': json.dumps({
                'provider': 'anthropic',
                'model': 'claude-sonnet-4-20250514',
                'temperature': 0.7,
                'max_tokens': 4000
            }),
            'generated_lessons': '[]',
            'generated_methods': '[]',
            'current_step': 'source_selection',
            'steps_completed': '[]'
        }

        params = {**defaults, **session_data}

        # Convert dicts to JSON strings
        for key in ['source_data', 'ai_config', 'generated_theory', 'generated_lessons', 'generated_methods', 'steps_completed']:
            if key in params and isinstance(params[key], (dict, list)):
                params[key] = json.dumps(params[key])

        return insert_returning(cls.table_name, params, returning='*')

    @classmethod
    def find_by_id(cls, session_id: str) -> Optional[Dict[str, Any]]:
        """Find session by ID"""
        query = """
            SELECT s.*,
                   u.email AS user_email,
                   c.title AS course_title,
                   ch.title AS chapter_title
            FROM ai_authoring_sessions s
            LEFT JOIN users u ON s.user_id = u.user_id
            LEFT JOIN courses c ON s.course_id = c.course_id
            LEFT JOIN chapters ch ON s.chapter_id = ch.chapter_id
            WHERE s.session_id = %s
        """
        return fetch_one(query, (session_id,))

    @classmethod
    def find_by_user(cls, user_id: str, limit: int = 20, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Find all sessions for a user"""
        if status:
            query = """
                SELECT s.*, c.title AS course_title
                FROM ai_authoring_sessions s
                LEFT JOIN courses c ON s.course_id = c.course_id
                WHERE s.user_id = %s AND s.status = %s
                ORDER BY s.last_activity_at DESC
                LIMIT %s
            """
            return fetch_all(query, (user_id, status, limit))
        else:
            query = """
                SELECT s.*, c.title AS course_title
                FROM ai_authoring_sessions s
                LEFT JOIN courses c ON s.course_id = c.course_id
                WHERE s.user_id = %s
                ORDER BY s.last_activity_at DESC
                LIMIT %s
            """
            return fetch_all(query, (user_id, limit))

    @classmethod
    def find_by_course(cls, course_id: str) -> List[Dict[str, Any]]:
        """Find all sessions for a course"""
        query = """
            SELECT s.*, u.email AS user_email
            FROM ai_authoring_sessions s
            LEFT JOIN users u ON s.user_id = u.user_id
            WHERE s.course_id = %s
            ORDER BY s.created_at DESC
        """
        return fetch_all(query, (course_id,))

    @classmethod
    def update_session(cls, session_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update session data"""
        # Convert dicts to JSON strings
        for key in ['source_data', 'ai_config', 'generated_theory', 'generated_lessons', 'generated_methods', 'steps_completed']:
            if key in data and isinstance(data[key], (dict, list)):
                data[key] = json.dumps(data[key])

        data['last_activity_at'] = datetime.utcnow()

        return update_returning(cls.table_name, data, 'session_id = %s', (session_id,), returning='*')

    @classmethod
    def update_status(cls, session_id: str, status: str) -> Optional[Dict[str, Any]]:
        """Update session status"""
        data = {'status': status, 'last_activity_at': datetime.utcnow()}
        if status == 'completed':
            data['completed_at'] = datetime.utcnow()
        return update_returning(cls.table_name, data, 'session_id = %s', (session_id,), returning='*')

    @classmethod
    def update_step(cls, session_id: str, step: str, completed_steps: List[str]) -> Optional[Dict[str, Any]]:
        """Update current step and completed steps"""
        data = {
            'current_step': step,
            'steps_completed': json.dumps(completed_steps),
            'last_activity_at': datetime.utcnow()
        }
        return update_returning(cls.table_name, data, 'session_id = %s', (session_id,), returning='*')

    @classmethod
    def save_generated_content(cls, session_id: str, content_type: str, content: Any) -> Optional[Dict[str, Any]]:
        """Save generated content (theory, lessons, methods)"""
        column_map = {
            'theory': 'generated_theory',
            'lessons': 'generated_lessons',
            'methods': 'generated_methods'
        }

        if content_type not in column_map:
            raise ValueError(f"Invalid content type: {content_type}")

        column = column_map[content_type]
        data = {
            column: json.dumps(content) if isinstance(content, (dict, list)) else content,
            'last_activity_at': datetime.utcnow()
        }

        return update_returning(cls.table_name, data, 'session_id = %s', (session_id,), returning='*')

    @classmethod
    def delete_session(cls, session_id: str) -> bool:
        """Delete a session"""
        query = "DELETE FROM ai_authoring_sessions WHERE session_id = %s"
        return execute_query(query, (session_id,))


class AISessionSnapshotRepository:
    """Repository for session snapshots (undo/redo)"""

    table_name = 'ai_session_snapshots'

    @classmethod
    def create_snapshot(cls, session_id: str, snapshot_data: Dict[str, Any], description: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Create a new snapshot"""
        # Get next sequence number
        query = "SELECT COALESCE(MAX(sequence_number), 0) + 1 AS next_seq FROM ai_session_snapshots WHERE session_id = %s"
        result = fetch_one(query, (session_id,))
        next_seq = result['next_seq'] if result else 1

        # Clear is_current from all existing snapshots
        execute_query("UPDATE ai_session_snapshots SET is_current = FALSE WHERE session_id = %s", (session_id,))

        params = {
            'session_id': session_id,
            'snapshot_data': json.dumps(snapshot_data),
            'description': description,
            'sequence_number': next_seq,
            'is_current': True
        }

        return insert_returning(cls.table_name, params, returning='*')

    @classmethod
    def get_snapshots(cls, session_id: str) -> List[Dict[str, Any]]:
        """Get all snapshots for a session"""
        query = """
            SELECT * FROM ai_session_snapshots
            WHERE session_id = %s
            ORDER BY sequence_number DESC
        """
        return fetch_all(query, (session_id,))

    @classmethod
    def get_current_snapshot(cls, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current snapshot"""
        query = "SELECT * FROM ai_session_snapshots WHERE session_id = %s AND is_current = TRUE"
        return fetch_one(query, (session_id,))

    @classmethod
    def restore_snapshot(cls, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """Restore to a specific snapshot"""
        # Get the snapshot
        query = "SELECT * FROM ai_session_snapshots WHERE snapshot_id = %s"
        snapshot = fetch_one(query, (snapshot_id,))

        if not snapshot:
            return None

        # Clear current and set this as current
        execute_query("UPDATE ai_session_snapshots SET is_current = FALSE WHERE session_id = %s", (snapshot['session_id'],))
        execute_query("UPDATE ai_session_snapshots SET is_current = TRUE WHERE snapshot_id = %s", (snapshot_id,))

        return snapshot


class AIGenerationVariantRepository:
    """Repository for AI generation variants"""

    table_name = 'ai_generation_variants'

    @classmethod
    def create_variant(cls, variant_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new variant"""
        # Get next variant index for this type
        query = """
            SELECT COALESCE(MAX(variant_index), -1) + 1 AS next_idx
            FROM ai_generation_variants
            WHERE session_id = %s AND variant_type = %s
        """
        result = fetch_one(query, (variant_data['session_id'], variant_data['variant_type']))
        next_idx = result['next_idx'] if result else 0

        params = {
            'session_id': variant_data['session_id'],
            'variant_type': variant_data['variant_type'],
            'variant_index': next_idx,
            'content': json.dumps(variant_data['content']) if isinstance(variant_data['content'], (dict, list)) else variant_data['content'],
            'ai_provider': variant_data.get('ai_provider'),
            'ai_model': variant_data.get('ai_model'),
            'prompt_used': variant_data.get('prompt_used'),
            'generation_params': json.dumps(variant_data.get('generation_params', {})),
            'is_selected': False,
            'generation_started_at': variant_data.get('generation_started_at'),
            'generation_completed_at': variant_data.get('generation_completed_at'),
            'generation_duration_ms': variant_data.get('generation_duration_ms')
        }

        return insert_returning(cls.table_name, params, returning='*')

    @classmethod
    def get_variants(cls, session_id: str, variant_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get variants for a session"""
        if variant_type:
            query = """
                SELECT * FROM ai_generation_variants
                WHERE session_id = %s AND variant_type = %s
                ORDER BY variant_index
            """
            return fetch_all(query, (session_id, variant_type))
        else:
            query = """
                SELECT * FROM ai_generation_variants
                WHERE session_id = %s
                ORDER BY variant_type, variant_index
            """
            return fetch_all(query, (session_id,))

    @classmethod
    def select_variant(cls, variant_id: str) -> Optional[Dict[str, Any]]:
        """Mark a variant as selected (deselects others of same type)"""
        # Get variant info
        variant = fetch_one("SELECT session_id, variant_type FROM ai_generation_variants WHERE variant_id = %s", (variant_id,))
        if not variant:
            return None

        # Deselect others of same type
        execute_query(
            "UPDATE ai_generation_variants SET is_selected = FALSE WHERE session_id = %s AND variant_type = %s",
            (variant['session_id'], variant['variant_type'])
        )

        # Select this one
        return update_returning(cls.table_name, {'is_selected': True}, 'variant_id = %s', (variant_id,), returning='*')

    @classmethod
    def rate_variant(cls, variant_id: str, rating: int, feedback: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Rate a variant"""
        data = {'user_rating': rating}
        if feedback:
            data['user_feedback'] = feedback
        return update_returning(cls.table_name, data, 'variant_id = %s', (variant_id,), returning='*')


class AIStudioAnalyticsRepository:
    """Repository for AI Studio analytics events"""

    table_name = 'ai_studio_analytics'

    @classmethod
    def log_event(cls, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Log an analytics event"""
        params = {
            'session_id': event_data.get('session_id'),
            'user_id': event_data.get('user_id'),
            'event_type': event_data['event_type'],
            'event_data': json.dumps(event_data.get('event_data', {})),
            'tokens_used': event_data.get('tokens_used'),
            'generation_time_ms': event_data.get('generation_time_ms'),
            'ai_provider': event_data.get('ai_provider'),
            'ai_model': event_data.get('ai_model'),
            'step_name': event_data.get('step_name'),
            'component_name': event_data.get('component_name')
        }
        return insert_returning(cls.table_name, params, returning='*')

    @classmethod
    def get_session_events(cls, session_id: str) -> List[Dict[str, Any]]:
        """Get all events for a session"""
        query = "SELECT * FROM ai_studio_analytics WHERE session_id = %s ORDER BY created_at DESC"
        return fetch_all(query, (session_id,))

    @classmethod
    def get_user_stats(cls, user_id: str) -> Dict[str, Any]:
        """Get usage stats for a user"""
        query = """
            SELECT
                COUNT(*) AS total_events,
                COALESCE(SUM(tokens_used), 0) AS total_tokens,
                COALESCE(AVG(generation_time_ms), 0) AS avg_generation_time,
                COUNT(DISTINCT session_id) AS total_sessions
            FROM ai_studio_analytics
            WHERE user_id = %s
        """
        return fetch_one(query, (user_id,)) or {
            'total_events': 0,
            'total_tokens': 0,
            'avg_generation_time': 0,
            'total_sessions': 0
        }


class PDFCacheRepository:
    """Repository for PDF text cache"""

    table_name = 'pdf_cache'

    @classmethod
    def get_by_hash(cls, file_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached PDF by file hash"""
        query = "SELECT * FROM pdf_cache WHERE file_hash = %s"
        result = fetch_one(query, (file_hash,))

        if result:
            # Update access stats
            execute_query(
                "UPDATE pdf_cache SET access_count = access_count + 1, last_accessed_at = NOW() WHERE file_hash = %s",
                (file_hash,)
            )

        return result

    @classmethod
    def create_cache(cls, cache_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create new cache entry"""
        params = {
            'file_hash': cache_data['file_hash'],
            'original_filename': cache_data.get('original_filename'),
            'file_size_bytes': cache_data.get('file_size_bytes'),
            'page_count': cache_data.get('page_count'),
            'extracted_text': cache_data.get('extracted_text'),
            'extracted_metadata': json.dumps(cache_data.get('extracted_metadata', {})),
            'structure_analysis': json.dumps(cache_data.get('structure_analysis', {})),
            'extraction_method': cache_data.get('extraction_method', 'pdfplumber'),
            'processing_time_ms': cache_data.get('processing_time_ms')
        }
        return insert_returning(cls.table_name, params, returning='*')

    @classmethod
    def calculate_file_hash(cls, file_content: bytes) -> str:
        """Calculate SHA-256 hash of file content"""
        return hashlib.sha256(file_content).hexdigest()


class AIAuthoringTemplateRepository:
    """Repository for authoring templates"""

    table_name = 'ai_authoring_templates'

    @classmethod
    def get_all_active(cls) -> List[Dict[str, Any]]:
        """Get all active templates"""
        query = "SELECT * FROM ai_authoring_templates WHERE is_active = TRUE ORDER BY category, template_name"
        return fetch_all(query)

    @classmethod
    def get_by_key(cls, template_key: str) -> Optional[Dict[str, Any]]:
        """Get template by key"""
        query = "SELECT * FROM ai_authoring_templates WHERE template_key = %s"
        result = fetch_one(query, (template_key,))

        if result:
            # Increment usage count
            execute_query(
                "UPDATE ai_authoring_templates SET usage_count = usage_count + 1 WHERE template_key = %s",
                (template_key,)
            )

        return result

    @classmethod
    def get_by_category(cls, category: str) -> List[Dict[str, Any]]:
        """Get templates by category"""
        query = "SELECT * FROM ai_authoring_templates WHERE category = %s AND is_active = TRUE ORDER BY template_name"
        return fetch_all(query, (category,))
