"""
Routing Overview Endpoints (DDD)

Read-only overview of LM model assignments.
"""

from flask import jsonify
from typing import Dict, Any, Tuple
import logging

from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.extensions import limiter
from app.repositories.lm_model_routing import (
    LMModelAssignmentRepository,
    LMModelRequirementsRepository
)
from app.ki.learning_method_mapping import get_method_by_id

from app.api.system_features.learning_methods.core.routing import (
    LMIDRange,
    RoutingStatsService
)

from . import lm_routing_overview_bp

logger = logging.getLogger(__name__)


@lm_routing_overview_bp.route('/overview', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
@limiter.limit("60 per minute")
def get_lm_routing_overview() -> Tuple[Dict[str, Any], int]:
    """
    Get overview of all learning methods with their model assignments.

    Returns:
        JSON response with assignments and stats

    DDD: Uses RoutingStatsService for statistics calculation
    """
    try:
        # Fetch data from repositories
        overview = LMModelAssignmentRepository.get_overview()
        requirements_list = LMModelRequirementsRepository.get_all_requirements()

        # Build requirements dict
        requirements = {
            r['learning_method_id']: r
            for r in requirements_list
        }

        # Build assignments list with enriched data
        assignments = []
        for row in overview:
            lm_id = row['learning_method_id']
            lm_def = get_method_by_id(lm_id)
            req = requirements.get(lm_id, {})

            is_configured = row.get('model_id') is not None

            assignments.append({
                'learning_method_id': lm_id,
                'lm_code': LMIDRange.format_code(lm_id),
                'lm_name': lm_def.name if lm_def else f'LM{lm_id}',
                'lm_group': lm_def.group.value if lm_def else None,
                'lm_type': lm_def.method_type.value if lm_def else None,
                'ki_usage': lm_def.ki_usage.value if lm_def else None,
                'model_required': req.get('required', True),
                'recommended_categories': req.get('recommended_categories', ['chat']),
                'requires_vision': req.get('requires_vision', False),
                'assignment_id': row.get('assignment_id'),
                'model_id': row.get('model_id'),
                'model_name': row.get('model_name'),
                'model_display_name': row.get('model_display_name'),
                'model_category': row.get('model_category'),
                'provider_name': row.get('provider_name'),
                'provider_display_name': row.get('provider_display_name'),
                'is_configured': is_configured
            })

        # DDD: Calculate stats using Service
        stats = RoutingStatsService.calculate_stats(
            assignments=overview,
            requirements=requirements,
            total_lms=LMIDRange.MAX + 1
        )

        return jsonify({
            'success': True,
            'data': {
                'assignments': assignments,
                'stats': stats.to_dict()
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting routing overview: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_OVERVIEW_ERROR',
                'message': str(e)
            }
        }), 500


@lm_routing_overview_bp.route('/unconfigured', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
@limiter.limit("60 per minute")
def get_unconfigured_lms() -> Tuple[Dict[str, Any], int]:
    """
    Get all learning methods that require a model but don't have one configured.

    Returns:
        JSON response with unconfigured LMs

    DDD: Filters LMs using business rules
    """
    try:
        unconfigured = LMModelAssignmentRepository.get_unconfigured_lms()

        result = []
        for row in unconfigured:
            lm_id = row['learning_method_id']
            lm_def = get_method_by_id(lm_id)

            result.append({
                'learning_method_id': lm_id,
                'lm_code': LMIDRange.format_code(lm_id),
                'lm_name': lm_def.name if lm_def else f'LM{lm_id}',
                'lm_group': lm_def.group.value if lm_def else None,
                'recommended_categories': row.get('recommended_categories', ['chat']),
                'description': row.get('description')
            })

        return jsonify({
            'success': True,
            'data': {
                'unconfigured': result,
                'count': len(result)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting unconfigured LMs: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_UNCONFIGURED_ERROR',
                'message': str(e)
            }
        }), 500


@lm_routing_overview_bp.route('/requirements', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
@limiter.limit("60 per minute")
def get_lm_requirements() -> Tuple[Dict[str, Any], int]:
    """
    Get all learning method requirements.

    Returns:
        JSON response with requirements for all LMs

    DDD: Exposes domain requirements
    """
    try:
        requirements = LMModelRequirementsRepository.get_all_requirements()

        result = []
        for req in requirements:
            lm_id = req['learning_method_id']
            lm_def = get_method_by_id(lm_id)

            result.append({
                'learning_method_id': lm_id,
                'lm_code': LMIDRange.format_code(lm_id),
                'lm_name': lm_def.name if lm_def else f'LM{lm_id}',
                'required': req.get('required', True),
                'recommended_categories': req.get('recommended_categories', ['chat']),
                'requires_vision': req.get('requires_vision', False),
                'requires_functions': req.get('requires_functions', False),
                'min_context_window': req.get('min_context_window'),
                'description': req.get('description')
            })

        return jsonify({
            'success': True,
            'data': {
                'requirements': result
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting LM requirements: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_REQUIREMENTS_ERROR',
                'message': str(e)
            }
        }), 500
