"""
i18n AI Generation Module
=========================
AI-powered translation generation using the configured default translation model.
"""

from typing import Optional, Dict, Any
from app.infrastructure.persistence.repositories.i18n.service_queries_part2 import (
    I18nAIQueriesRepository,
)
import logging

logger = logging.getLogger(__name__)


class AITranslationGenerator:
    """Manages AI-powered translation generation."""

    @staticmethod
    def generate_ai_translation(
        key_id: str,
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
        from app.application.services.ai.adapter import AIAdapter
        from app.infrastructure.persistence.repositories.ai_models.defaults import AIModelsDefaultRepository

        try:
            # Get key info and primary language source
            key_info = I18nAIQueriesRepository.get_key_with_source(key_id, primary_language)

            if not key_info or not key_info.get('source_value'):
                return {'success': False, 'error': f'No {primary_language.upper()} source text found'}

            # Get target language info
            lang_info = I18nAIQueriesRepository.get_language_info(target_language)

            if not lang_info:
                return {'success': False, 'error': 'Target language not found'}

            # Resolve AI model from admin settings — NO fallback
            model_info = AIModelsDefaultRepository.get_default_model('translation')
            if not model_info:
                return {'success': False, 'error': 'No default translation model configured. Configure in AI Settings.'}

            provider = model_info['provider_name']
            model_name = model_info['model_name']
            source_lang_name = key_info.get('source_language_name', 'German')

            # Build AI prompt
            prompt = f"""Translate the following {source_lang_name} text to {lang_info['language_name']} ({lang_info['native_name']}).

Context: This is a UI text for key "{key_info['key_path']}" in namespace "{key_info['namespace_code']}".
{f"Description: {key_info['description']}" if key_info.get('description') else ""}
{f"Context hint: {key_info['context_hint']}" if key_info.get('context_hint') else ""}

{source_lang_name} text:
{key_info['source_value']}

IMPORTANT:
- Keep any placeholders like {{name}}, {{count}}, etc. unchanged
- Match the tone and formality of the original
- Keep it concise - this is UI text
- Return ONLY the translated text, nothing else"""

            # Call AI via adapter
            adapter = AIAdapter(provider=provider, model=model_name)
            result = adapter.send_request(
                prompt=prompt,
                language=target_language,
                max_tokens=500,
                temperature=0.3
            )

            if result and result.get('output_text'):
                translated_text = result['output_text'].strip()

                # Save translation if callback provided
                if set_translation_fn:
                    set_translation_fn(
                        key_id=key_id,
                        language_code=target_language,
                        translated_value=translated_text,
                        translator_user_id=user_id,
                        translation_source='llm'
                    )

                return {
                    'success': True,
                    'translation': translated_text,
                    'tokens_used': result.get('total_tokens', 0),
                    'cost_eur': result.get('cost_eur', 0)
                }

            return {'success': False, 'error': 'AI generation returned empty result'}

        except Exception as e:
            logger.error(f"Error generating AI translation: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def bulk_generate_translations(
        target_language: str,
        namespace_code: Optional[str] = None,
        user_id: str = None,
        limit: int = 50,
        primary_language: str = 'de',
        generate_fn=None
    ) -> Dict[str, Any]:
        """
        Generate AI translations for multiple missing keys.

        Args:
            target_language: Target language code
            namespace_code: Optional namespace filter
            user_id: Requesting user ID
            limit: Max keys to generate
            primary_language: Source language code
            generate_fn: Optional callback for generate_ai_translation

        Returns:
            Summary dict with success count, failures, and token usage
        """
        try:
            # Find keys missing translations for target language
            missing_keys = I18nAIQueriesRepository.get_untranslated_keys(
                target_language=target_language,
                primary_language=primary_language,
                namespace_code=namespace_code,
                limit=limit
            )

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
