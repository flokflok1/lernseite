"""
Admin Translations API — Part 2: Bulk Translate
================================================
AI-powered bulk translation using step-based job execution.

Routes registered on the blueprint from translations.py.
"""

from flask import request, jsonify, g
from app.api.middleware.auth import token_required, admin_required
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all
from app.application.services.i18n.translations import TranslationManager
from app.api.v1.panel.admin.i18n.translations.translations import bp
import json
import logging

logger = logging.getLogger(__name__)


def _parse_json_field(field) -> dict:
    """Parse a JSONB field that may be dict or JSON string."""
    if isinstance(field, str):
        return json.loads(field)
    return field or {}


def _extract_job_params(input_data: dict) -> tuple:
    """
    Extract source_language, target_language, namespace_code from job input_data.

    Handles both direct fields and legacy 'prompt' JSON string.

    Returns:
        (source_language, target_language, namespace_code)
    """
    source_lang = input_data.get('source_language', '')
    target_lang = input_data.get('target_language', '')
    ns_filter = input_data.get('namespace_code')

    # Legacy: create_job stores input_prompt in input_data.prompt
    if not target_lang and 'prompt' in input_data:
        try:
            parsed = json.loads(input_data['prompt'])
            source_lang = parsed.get('source_language', 'en')
            target_lang = parsed.get('target_language', '')
            ns_filter = parsed.get('namespace_code')
        except (json.JSONDecodeError, TypeError):
            pass

    return source_lang, target_lang, ns_filter


# ---------------------------------------------------------------------------
# Endpoint 1: Create bulk translation job
# ---------------------------------------------------------------------------

@bp.route('/bulk-translate', methods=['POST'])
@token_required
@admin_required
def create_bulk_translate_job():
    """
    Create a bulk translation job.

    Request Body:
        {
            "source_language": "en",
            "target_language": "fr",
            "namespace_code": null
        }

    Returns:
        { job_id, status, total }
    """
    from app.application.services.ai.job_service import AIJobService
    from app.infrastructure.persistence.repositories.ai.jobs import AIJobRepository

    data = request.get_json(silent=True) or {}
    source_language = data.get('source_language', 'en')
    target_language = data.get('target_language')

    if not target_language:
        return jsonify({'success': False, 'error': 'target_language required'}), 400
    if source_language == target_language:
        return jsonify({'success': False, 'error': 'source and target language must differ'}), 400

    namespace_code = data.get('namespace_code')

    # Count keys needing translation
    count_query = """
        SELECT COUNT(*) AS total
        FROM translations.i18n_keys k
        WHERE k.is_active = TRUE
        AND EXISTS (
            SELECT 1 FROM translations.i18n_translations t
            WHERE t.key_id = k.key_id AND t.language_code = %s
        )
        AND NOT EXISTS (
            SELECT 1 FROM translations.i18n_translations t
            WHERE t.key_id = k.key_id AND t.language_code = %s
        )
    """
    params = [source_language, target_language]
    if namespace_code:
        count_query += " AND k.namespace_code = %s"
        params.append(namespace_code)

    count_result = fetch_one(count_query, tuple(params))
    total = count_result['total'] if count_result else 0

    if total == 0:
        return jsonify({'success': True, 'job_id': None, 'status': 'completed', 'total': 0}), 200

    # Create AI job
    job = AIJobService.create_job(
        user_id=g.user_id,
        job_type='translation',
        input_prompt=json.dumps({
            'source_language': source_language,
            'target_language': target_language,
            'namespace_code': namespace_code,
        }),
    )

    # Store initial output_data with counters
    AIJobRepository.update_output(job['id'], {
        'total': total,
        'translated': 0,
        'failed': 0,
        'offset': 0,
        'tokens_used': 0,
    })

    return jsonify({
        'success': True,
        'job_id': job['id'],
        'status': 'queued',
        'total': total,
    }), 201


# ---------------------------------------------------------------------------
# Endpoint 2: Execute next translation step (idempotent/resumable)
# ---------------------------------------------------------------------------

@bp.route('/bulk-translate/<job_id>/run', methods=['POST'])
@token_required
@admin_required
def run_bulk_translate_step(job_id: str):
    """
    Execute next translation step (processes a batch of keys).

    Safe to call repeatedly (idempotent/resumable).
    Frontend drives by calling this until status is completed/failed.
    """
    from app.infrastructure.persistence.repositories.ai.jobs import AIJobRepository
    from app.infrastructure.persistence.repositories.ai_models.defaults import AIModelsDefaultRepository
    from app.application.services.ai.adapter import AIAdapter
    from app.application.services.ai.job_service import AIJobService

    job = AIJobRepository.find_by_id(job_id)
    if not job:
        return jsonify({'success': False, 'error': 'Job not found'}), 404

    # Idempotent: already terminal state
    if job['status'] in ('completed', 'failed', 'cancelled'):
        return jsonify({
            'success': True,
            'job_id': job_id,
            'status': job['status'],
            'progress_percentage': job.get('progress_percentage', 0),
            'output_data': _parse_json_field(job.get('output_data')),
        }), 200

    # Transition queued -> processing
    if job['status'] == 'queued':
        AIJobService.start_processing(job_id)

    input_data = _parse_json_field(job.get('input_data'))
    output_data = _parse_json_field(job.get('output_data'))

    source_lang, target_lang, ns_filter = _extract_job_params(input_data)

    if not target_lang:
        AIJobRepository.fail_job(job_id, 'Missing target_language in job input_data')
        return jsonify({'success': False, 'error': 'Invalid job configuration'}), 400

    # Resolve AI model — NO fallback
    model_info = AIModelsDefaultRepository.get_default_model('translation')
    if not model_info:
        AIJobRepository.fail_job(job_id, 'No default translation model configured')
        return jsonify({
            'success': False,
            'error': 'No default translation model configured. Configure in AI Settings.',
        }), 409

    provider = model_info['provider_name']
    model_name = model_info['model_name']

    translated_count = output_data.get('translated', 0)
    failed_count = output_data.get('failed', 0)
    total = output_data.get('total', 1)
    tokens_used = output_data.get('tokens_used', 0)
    BATCH_SIZE = 50

    # Fetch next batch of keys needing translation
    batch_query = """
        SELECT k.key_id, k.key_path, k.namespace_code,
               t.translated_value AS source_value
        FROM translations.i18n_keys k
        JOIN translations.i18n_translations t
            ON t.key_id = k.key_id AND t.language_code = %s
        WHERE k.is_active = TRUE
        AND NOT EXISTS (
            SELECT 1 FROM translations.i18n_translations t2
            WHERE t2.key_id = k.key_id AND t2.language_code = %s
        )
    """
    batch_params = [source_lang, target_lang]
    if ns_filter:
        batch_query += " AND k.namespace_code = %s"
        batch_params.append(ns_filter)
    batch_query += " ORDER BY k.namespace_code, k.key_path LIMIT %s"
    batch_params.append(BATCH_SIZE)

    keys = fetch_all(batch_query, tuple(batch_params)) or []

    if not keys:
        # No more keys → mark completed
        final_output = {**output_data, 'translated': translated_count, 'failed': failed_count, 'tokens_used': tokens_used}
        AIJobRepository.complete_job(job_id, final_output)
        return jsonify({
            'success': True, 'job_id': job_id, 'status': 'completed',
            'progress_percentage': 100, 'output_data': final_output,
        }), 200

    # Get target language name for prompt
    lang_info = fetch_one(
        "SELECT language_name FROM translations.supported_languages WHERE language_code = %s",
        (target_lang,)
    )
    target_lang_name = lang_info['language_name'] if lang_info else target_lang

    # Translate each key individually
    try:
        adapter = AIAdapter(provider=provider, model=model_name)
        for key in keys:
            try:
                prompt = (
                    f"Translate this UI text to {target_lang_name}.\n\n"
                    f"Key: {key['key_path']}\n"
                    f"Namespace: {key['namespace_code']}\n"
                    f"Source text: {key['source_value']}\n\n"
                    "IMPORTANT: Return ONLY the translated text, nothing else. "
                    "Keep placeholders like {{name}} unchanged."
                )
                result = adapter.send_request(
                    prompt=prompt, language=target_lang,
                    max_tokens=500, temperature=0.3,
                )
                if result and result.get('output_text'):
                    TranslationManager.set_translation(
                        key_id=str(key['key_id']),
                        language_code=target_lang,
                        translated_value=result['output_text'].strip(),
                        translator_user_id=g.user_id,
                        translation_source='llm',
                    )
                    translated_count += 1
                    tokens_used += result.get('total_tokens', 0)
                else:
                    failed_count += 1
            except Exception as e:
                logger.warning(f"Translation failed for key {key['key_path']}: {e}")
                failed_count += 1
    except Exception as e:
        AIJobRepository.fail_job(job_id, str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

    # Update progress
    done = translated_count + failed_count
    progress = min(int((done / total) * 100), 99) if total > 0 else 100
    new_output = {
        'total': total, 'translated': translated_count,
        'failed': failed_count, 'offset': done, 'tokens_used': tokens_used,
    }
    AIJobRepository.update_output(job_id, new_output)
    AIJobRepository.update_progress(job_id, progress)

    if done >= total:
        AIJobRepository.complete_job(job_id, new_output)
        progress = 100

    return jsonify({
        'success': True,
        'job_id': job_id,
        'status': 'completed' if done >= total else 'processing',
        'progress_percentage': progress,
        'output_data': new_output,
    }), 200


# ---------------------------------------------------------------------------
# Endpoint 3: Poll job progress
# ---------------------------------------------------------------------------

@bp.route('/bulk-translate/<job_id>', methods=['GET'])
@token_required
@admin_required
def get_bulk_translate_progress(job_id: str):
    """Poll bulk translation job status/progress."""
    from app.infrastructure.persistence.repositories.ai.jobs import AIJobRepository

    job = AIJobRepository.find_by_id(job_id)
    if not job:
        return jsonify({'success': False, 'error': 'Job not found'}), 404

    return jsonify({
        'success': True,
        'job_id': job_id,
        'status': job['status'],
        'progress_percentage': job.get('progress_percentage', 0),
        'input_data': _parse_json_field(job.get('input_data')),
        'output_data': _parse_json_field(job.get('output_data')),
    }), 200
