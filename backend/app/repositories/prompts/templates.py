"""
LernsystemX - Prompt Template Repository

Database access for editable prompt templates.
Allows admins to customize AI prompts without code changes.

The system uses a fallback hierarchy:
1. DB Override (if exists and is_active)
2. Code-based default (from prompt_registry.py)

This means admins can customize prompts in the UI, while code-based
defaults serve as fallback.

Phase KI-Studio Enhancement
"""

from typing import Optional, List, Dict, Any
import logging
import json

from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class PromptTemplateRepository(BaseRepository):
    """
    Repository for prompt templates stored in database.

    Provides CRUD operations for prompt templates and supports
    the fallback system with code-based defaults.
    """

    @staticmethod
    def find_by_code(code: str) -> Optional[Dict[str, Any]]:
        """
        Find a prompt template by its unique code.

        Args:
            code: Unique template identifier (e.g., 'theory_sheet_adhs')

        Returns:
            Template dict or None if not found
        """
        query = """
            SELECT
                template_id, code, category, style,
                title, description, icon,
                system_prompt, user_prompt_template,
                model, provider, temperature, max_tokens,
                variables, output_format, output_schema,
                tts_enabled, tts_voice, tts_model, tts_speed,
                language, target_audience, difficulty_level,
                lm_type, is_active, is_default, is_system,
                version, created_at, updated_at
            FROM ai_pipeline.prompt_templates
            WHERE code = %s AND is_active = true
        """
        return PromptTemplateRepository.fetch_one(query, (code,))

    @staticmethod
    def find_by_id(template_id: str) -> Optional[Dict[str, Any]]:
        """Find a template by its UUID."""
        query = """
            SELECT *
            FROM ai_pipeline.prompt_templates
            WHERE template_id = %s
        """
        return PromptTemplateRepository.fetch_one(query, (template_id,))

    @staticmethod
    def find_by_category_and_style(category: str, style: str = 'standard') -> Optional[Dict[str, Any]]:
        """
        Find the default template for a category and style.

        Args:
            category: Template category ('theory', 'lesson', 'quiz', etc.)
            style: Style variant ('standard', 'adhs', 'short', 'detailed', 'exam_focus')

        Returns:
            Default template for this category+style or None
        """
        query = """
            SELECT *
            FROM ai_pipeline.prompt_templates
            WHERE category = %s AND style = %s AND is_active = true
            ORDER BY is_default DESC, created_at DESC
            LIMIT 1
        """
        return PromptTemplateRepository.fetch_one(query, (category, style))

    @staticmethod
    def list_by_category(category: str) -> List[Dict[str, Any]]:
        """
        List all active templates for a category.

        Args:
            category: Template category

        Returns:
            List of templates for this category
        """
        query = """
            SELECT
                template_id, code, category, style,
                title, description, icon,
                tts_enabled, is_default, is_system,
                created_at, updated_at
            FROM ai_pipeline.prompt_templates
            WHERE category = %s AND is_active = true
            ORDER BY style, is_default DESC, title
        """
        return PromptTemplateRepository.fetch_all(query, (category,))

    @staticmethod
    def list_all_active() -> List[Dict[str, Any]]:
        """List all active templates."""
        query = """
            SELECT
                template_id, code, category, style,
                title, description, icon,
                model, provider,
                tts_enabled, is_default, is_system,
                version, created_at, updated_at
            FROM ai_pipeline.prompt_templates
            WHERE is_active = true
            ORDER BY category, style, title
        """
        return PromptTemplateRepository.fetch_all(query)

    @staticmethod
    def list_styles_for_category(category: str) -> List[Dict[str, Any]]:
        """
        Get available styles for a category.

        Returns:
            List of dicts with style info
        """
        query = """
            SELECT DISTINCT
                style,
                COUNT(*) as template_count,
                BOOL_OR(is_default) as has_default
            FROM ai_pipeline.prompt_templates
            WHERE category = %s AND is_active = true
            GROUP BY style
            ORDER BY style
        """
        return PromptTemplateRepository.fetch_all(query, (category,))

    @staticmethod
    def create(template_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new prompt template.

        Args:
            template_data: Template data dict

        Returns:
            Created template or None
        """
        # Convert dict fields to JSONB
        variables = template_data.get('variables', [])
        if isinstance(variables, list):
            variables = json.dumps(variables)

        output_schema = template_data.get('output_schema')
        if output_schema and isinstance(output_schema, dict):
            output_schema = json.dumps(output_schema)

        query = """
            INSERT INTO prompt_templates (
                code, category, style,
                title, description, icon,
                system_prompt, user_prompt_template,
                model, provider, temperature, max_tokens,
                variables, output_format, output_schema,
                tts_enabled, tts_voice, tts_model, tts_speed,
                language, target_audience, difficulty_level,
                lm_type, is_active, is_default, is_system,
                created_by
            ) VALUES (
                %s, %s, %s,
                %s, %s, %s,
                %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s,
                %s
            )
            RETURNING *
        """
        params = (
            template_data.get('code'),
            template_data.get('category'),
            template_data.get('style', 'standard'),
            template_data.get('title'),
            template_data.get('description'),
            template_data.get('icon'),
            template_data.get('system_prompt'),
            template_data.get('user_prompt_template'),
            template_data.get('model', 'gpt-4o-mini'),
            template_data.get('provider', 'openai'),
            template_data.get('temperature', 0.7),
            template_data.get('max_tokens', 4000),
            variables,
            template_data.get('output_format', 'json'),
            output_schema,
            template_data.get('tts_enabled', False),
            template_data.get('tts_voice', 'alloy'),
            template_data.get('tts_model', 'tts-1'),
            template_data.get('tts_speed', 1.0),
            template_data.get('language', 'de'),
            template_data.get('target_audience'),
            template_data.get('difficulty_level'),
            template_data.get('lm_type'),
            template_data.get('is_active', True),
            template_data.get('is_default', False),
            template_data.get('is_system', False),
            template_data.get('created_by')
        )
        return PromptTemplateRepository.fetch_one(query, params)

    @staticmethod
    def update(template_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing template.

        Note: System templates (is_system=true) cannot have their
        code or category changed.

        Args:
            template_id: Template UUID
            update_data: Fields to update

        Returns:
            Updated template or None
        """
        # Build dynamic update query
        allowed_fields = [
            'title', 'description', 'icon',
            'system_prompt', 'user_prompt_template',
            'model', 'provider', 'temperature', 'max_tokens',
            'variables', 'output_format', 'output_schema',
            'tts_enabled', 'tts_voice', 'tts_model', 'tts_speed',
            'language', 'target_audience', 'difficulty_level',
            'is_active', 'is_default',
            'updated_by'
        ]

        set_clauses = []
        params = []

        for field in allowed_fields:
            if field in update_data:
                value = update_data[field]

                # Convert dict/list to JSON
                if field in ('variables', 'output_schema') and isinstance(value, (dict, list)):
                    value = json.dumps(value)

                set_clauses.append(f"{field} = %s")
                params.append(value)

        if not set_clauses:
            return PromptTemplateRepository.find_by_id(template_id)

        # Add version increment
        set_clauses.append("version = version + 1")

        params.append(template_id)

        query = f"""
            UPDATE ai_pipeline.prompt_templates
            SET {', '.join(set_clauses)}, updated_at = NOW()
            WHERE template_id = %s
            RETURNING *
        """
        return PromptTemplateRepository.fetch_one(query, tuple(params))

    @staticmethod
    def delete(template_id: str) -> bool:
        """
        Delete a template (soft delete by setting is_active=false).

        System templates cannot be deleted.

        Args:
            template_id: Template UUID

        Returns:
            True if deleted, False if not found or system template
        """
        query = """
            UPDATE ai_pipeline.prompt_templates
            SET is_active = false, updated_at = NOW()
            WHERE template_id = %s AND is_system = false
            RETURNING template_id
        """
        result = PromptTemplateRepository.fetch_one(query, (template_id,))
        return result is not None

    @staticmethod
    def set_default(template_id: str, category: str, style: str) -> bool:
        """
        Set a template as default for its category+style.

        Removes default flag from other templates in same category+style.

        Args:
            template_id: Template to set as default
            category: Template category
            style: Template style

        Returns:
            True if successful
        """
        # First, unset any existing default
        query1 = """
            UPDATE ai_pipeline.prompt_templates
            SET is_default = false
            WHERE category = %s AND style = %s AND is_default = true
        """
        PromptTemplateRepository.execute(query1, (category, style))

        # Then set new default
        query2 = """
            UPDATE ai_pipeline.prompt_templates
            SET is_default = true
            WHERE template_id = %s
            RETURNING template_id
        """
        result = PromptTemplateRepository.fetch_one(query2, (template_id,))
        return result is not None

    @staticmethod
    def duplicate(template_id: str, new_code: str, created_by: str = None) -> Optional[Dict[str, Any]]:
        """
        Duplicate a template with a new code.

        Args:
            template_id: Source template UUID
            new_code: Code for the new template
            created_by: User ID creating the duplicate

        Returns:
            New template or None
        """
        query = """
            INSERT INTO prompt_templates (
                code, category, style,
                title, description, icon,
                system_prompt, user_prompt_template,
                model, provider, temperature, max_tokens,
                variables, output_format, output_schema,
                tts_enabled, tts_voice, tts_model, tts_speed,
                language, target_audience, difficulty_level,
                lm_type, is_active, is_default, is_system,
                created_by
            )
            SELECT
                %s, category, style,
                title || ' (Kopie)', description, icon,
                system_prompt, user_prompt_template,
                model, provider, temperature, max_tokens,
                variables, output_format, output_schema,
                tts_enabled, tts_voice, tts_model, tts_speed,
                language, target_audience, difficulty_level,
                lm_type, true, false, false,
                %s
            FROM ai_pipeline.prompt_templates
            WHERE template_id = %s
            RETURNING *
        """
        return PromptTemplateRepository.fetch_one(query, (new_code, created_by, template_id))

    @staticmethod
    def log_usage(
        template_id: str,
        user_id: str,
        content_type: str,
        content_id: str = None,
        tokens_input: int = None,
        tokens_output: int = None,
        cost_eur: float = None,
        response_time_ms: int = None,
        tts_generated: bool = False,
        tts_duration_seconds: float = None,
        tts_cost_eur: float = None,
        context_data: Dict = None
    ) -> Optional[Dict[str, Any]]:
        """
        Log template usage for analytics.

        Args:
            template_id: Template used
            user_id: User who used it
            content_type: What was generated ('chapter_theory', 'lesson_steps', etc.)
            content_id: Reference to generated content
            tokens_input: Input tokens used
            tokens_output: Output tokens generated
            cost_eur: Total cost
            response_time_ms: Generation time
            tts_generated: Whether TTS was generated
            tts_duration_seconds: Audio duration
            tts_cost_eur: TTS cost
            context_data: Variables used

        Returns:
            Usage record or None
        """
        query = """
            INSERT INTO prompt_template_usage (
                template_id, user_id, content_type, content_id,
                tokens_input, tokens_output, tokens_total, cost_eur,
                response_time_ms,
                tts_generated, tts_duration_seconds, tts_cost_eur,
                context_data
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s,
                %s, %s, %s,
                %s
            )
            RETURNING usage_id
        """

        tokens_total = None
        if tokens_input is not None and tokens_output is not None:
            tokens_total = tokens_input + tokens_output

        context_json = json.dumps(context_data) if context_data else None

        return PromptTemplateRepository.fetch_one(query, (
            template_id, user_id, content_type, content_id,
            tokens_input, tokens_output, tokens_total, cost_eur,
            response_time_ms,
            tts_generated, tts_duration_seconds, tts_cost_eur,
            context_json
        ))

    @staticmethod
    def get_usage_stats(template_id: str = None, days: int = 30) -> Dict[str, Any]:
        """
        Get usage statistics for a template or all templates.

        Args:
            template_id: Optional template to filter by
            days: Number of days to look back

        Returns:
            Statistics dict
        """
        if template_id:
            query = """
                SELECT
                    COUNT(*) as total_uses,
                    SUM(tokens_total) as total_tokens,
                    SUM(cost_eur) as total_cost,
                    AVG(response_time_ms) as avg_response_time,
                    COUNT(CASE WHEN tts_generated THEN 1 END) as tts_count,
                    SUM(tts_cost_eur) as total_tts_cost
                FROM prompt_template_usage
                WHERE template_id = %s
                  AND created_at >= NOW() - INTERVAL '%s days'
            """
            result = PromptTemplateRepository.fetch_one(query, (template_id, days))
        else:
            query = """
                SELECT
                    COUNT(*) as total_uses,
                    SUM(tokens_total) as total_tokens,
                    SUM(cost_eur) as total_cost,
                    AVG(response_time_ms) as avg_response_time,
                    COUNT(CASE WHEN tts_generated THEN 1 END) as tts_count,
                    SUM(tts_cost_eur) as total_tts_cost,
                    COUNT(DISTINCT template_id) as templates_used
                FROM prompt_template_usage
                WHERE created_at >= NOW() - INTERVAL '%s days'
            """
            result = PromptTemplateRepository.fetch_one(query, (days,))

        return result or {}
