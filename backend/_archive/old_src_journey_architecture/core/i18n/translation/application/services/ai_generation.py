"""
i18n AI Generation Module
=========================
AI-powered translation generation using Anthropic Claude.
"""

from typing import Optional, Dict, Any
from src.database.connection import fetch_one, fetch_all
import logging

logger = logging.getLogger(__name__)


class AITranslationGenerator:
    """Manages AI-powered translation generation."""

    @staticmethod
    def generate_ai_translation(
        key_id: int,
        target_language: str,
        user_id: str,
        primary_language: str = 'de',
        set_translation_fn=None
    ) -> Optional[Dict[str, Any]]:
        """
        Generate AI translation for a key.

        Args:
            key_id: The translation key ID
            target_language: Target language code
            user_id: Requesting user ID
            primary_language: Source language code
            set_translation_fn: Optional callback to save translation

        Returns:
            Result dict with success status and translation or error
        """
        from src.services.ai_adapter import AIAdapter

        try:
            # Get key info and primary language source
            key_query = """
                SELECT
                    k.key_path,
                    k.context as description,
                    k.context as context_hint,
                    k.placeholders,
                    n.namespace_code,
                    t.value as source_value,
                    sl.language_name as source_language_name
                FROM i18n_keys k
                LEFT JOIN i18n_namespaces n ON k.namespace_id = n.namespace_id
                LEFT JOIN i18n_translations t ON k.key_id = t.key_id AND t.language_code = %s
                LEFT JOIN supported_languages sl ON sl.language_code = %s
                WHERE k.key_id = %s
            """
            key_info = fetch_one(key_query, (primary_language, primary_language, key_id))

            if not key_info or not key_info.get('source_value'):
                return {'success': False, 'error': f'No {primary_language.upper()} source text found'}

            # Get target language info
            lang_query = "SELECT language_name, native_name FROM supported_languages WHERE language_code = %s"
            lang_info = fetch_one(lang_query, (target_language,))

            if not lang_info:
                return {'success': False, 'error': 'Target language not found'}

            source_lang_name = key_info.get('source_language_name', 'German')

            # Build AI prompt
            prompt = f"""Translate the following {source_lang_name} text to {lang_info['language_name']} ({lang_info['native_name']}).

Context: This is a UI text for key "{key_info['key_path']}" in namespace "{key_info['namespace_code']}".
{f"Description: {key_info['description']}" if key_info.get('description') else ""}
{f"Context hint: {key_info['context_hint']}" if key_info.get('context_hint') else ""}
{f"Placeholders to preserve: {key_info['placeholders']}" if key_info.get('placeholders') else ""}

{source_lang_name} text:
{key_info['source_value']}

IMPORTANT:
- Keep any placeholders like {{name}}, {{count}}, etc. unchanged
- Match the tone and formality of the original
- Keep it concise - this is UI text
- Return ONLY the translated text, nothing else"""

            # Call AI
            result = AIAdapter.generate_content(
                prompt=prompt,
                provider='anthropic',
                user_id=user_id,
                max_tokens=500
            )

            if result and result.get('content'):
                translated_text = result['content'].strip()

                # Save translation if callback provided
                if set_translation_fn:
                    set_translation_fn(
                        key_id=key_id,
                        language_code=target_language,
                        value=translated_text,
                        translator_id=user_id,
                        is_machine_translated=True
                    )

                return {
                    'success': True,
                    'translation': translated_text,
                    'tokens_used': result.get('tokens_used', 0)
                }

            return {'success': False, 'error': 'AI generation failed'}

        except Exception as e:
            logger.error(f"Error generating AI translation: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def bulk_generate_translations(
        target_language: str,
        namespace_id: Optional[int] = None,
        user_id: str = None,
        limit: int = 50,
        primary_language: str = 'de',
        generate_fn=None
    ) -> Dict[str, Any]:
        """
        Generate AI translations for multiple missing keys.

        Args:
            target_language: Target language code
            namespace_id: Optional namespace filter
            user_id: Requesting user ID
            limit: Max keys to generate
            primary_language: Source language code
            generate_fn: Optional callback for generate_ai_translation

        Returns:
            Summary dict with success count, failures, and token usage
        """
        try:
            # Find keys missing translations for target language
            query = """
                SELECT k.key_id, k.key_path
                FROM i18n_keys k
                WHERE NOT EXISTS (
                    SELECT 1 FROM i18n_translations t
                    WHERE t.key_id = k.key_id AND t.language_code = %s
                )
                AND EXISTS (
                    SELECT 1 FROM i18n_translations t
                    WHERE t.key_id = k.key_id AND t.language_code = %s
                )
            """
            params = [target_language, primary_language]

            if namespace_id:
                query += " AND k.namespace_id = %s"
                params.append(namespace_id)

            query += " LIMIT %s"
            params.append(limit)

            missing_keys = fetch_all(query, tuple(params)) or []

            results = {
                'total': len(missing_keys),
                'success': 0,
                'failed': 0,
                'tokens_used': 0,
                'details': []
            }

            if not generate_fn:
                generate_fn = AITranslationGenerator.generate_ai_translation

            for key in missing_keys:
                result = generate_fn(
                    key_id=key['key_id'],
                    target_language=target_language,
                    user_id=user_id,
                    primary_language=primary_language
                )

                if result and result.get('success'):
                    results['success'] += 1
                    results['tokens_used'] += result.get('tokens_used', 0)
                else:
                    results['failed'] += 1

                results['details'].append({
                    'key_path': key['key_path'],
                    'success': result.get('success', False) if result else False,
                    'error': result.get('error') if result else 'Unknown error'
                })

            return results

        except Exception as e:
            logger.error(f"Error in bulk translation: {e}")
            return {'error': str(e)}
