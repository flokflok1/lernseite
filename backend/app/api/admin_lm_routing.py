"""
LernsystemX Admin LM Model Routing API

Learning Method to AI Model assignment endpoints:
- GET /api/v1/admin/lm-routing/overview - Get all LM assignments overview
- GET /api/v1/admin/lm-routing/unconfigured - Get unconfigured required LMs
- GET /api/v1/admin/lm-routing/requirements - Get all LM requirements
- GET /api/v1/admin/lm-routing/<lm_id> - Get assignment for specific LM
- PUT /api/v1/admin/lm-routing/<lm_id> - Set system-level assignment
- DELETE /api/v1/admin/lm-routing/<lm_id> - Remove system-level assignment
- POST /api/v1/admin/lm-routing/bulk - Bulk set assignments
- POST /api/v1/admin/lm-routing/resolve - Resolve model for LM with context

Phase KI-Architektur - Model Routing System
"""

from flask import request, jsonify, g, current_app

from app.api import api_v1
from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.repositories.lm_model_routing_repository import (
    LMModelAssignmentRepository,
    LMModelRequirementsRepository
)
from app.database.connection import fetch_all
from app.services.audit_service import AuditService
from app.ki.learning_method_mapping import LEARNING_METHODS, get_method_by_id


# ============================================================================
# LM Model Routing Overview
# ============================================================================

@api_v1.route('/admin/lm-routing/overview', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_lm_routing_overview():
    """
    Get overview of all learning methods with their model assignments.

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "assignments": [
                {
                    "learning_method_id": 0,
                    "lm_name": "Deep Explanation",
                    "lm_group": "A",
                    "model_required": true,
                    "model_id": 1,
                    "model_name": "gpt-4o",
                    "provider_name": "openai",
                    "is_configured": true
                },
                ...
            ],
            "stats": {
                "total": 33,
                "configured": 10,
                "unconfigured_required": 15,
                "unconfigured_optional": 8
            }
        }
    }
    ```
    """
    try:
        # Get overview from view
        overview = LMModelAssignmentRepository.get_overview()

        # Get requirements
        requirements = {
            r['learning_method_id']: r
            for r in LMModelRequirementsRepository.get_all_requirements()
        }

        # Build response with LM names from mapping
        assignments = []
        configured_count = 0
        unconfigured_required = 0
        unconfigured_optional = 0

        for row in overview:
            lm_id = row['learning_method_id']
            lm_def = get_method_by_id(lm_id)
            req = requirements.get(lm_id, {})

            is_configured = row.get('model_id') is not None
            is_required = req.get('required', True)

            if is_configured:
                configured_count += 1
            elif is_required:
                unconfigured_required += 1
            else:
                unconfigured_optional += 1

            assignments.append({
                'learning_method_id': lm_id,
                'lm_code': f'LM{str(lm_id).zfill(2)}',
                'lm_name': lm_def.name if lm_def else f'LM{lm_id}',
                'lm_group': lm_def.group.value if lm_def else None,
                'lm_type': lm_def.method_type.value if lm_def else None,
                'ki_usage': lm_def.ki_usage.value if lm_def else None,
                'model_required': is_required,
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

        return jsonify({
            'success': True,
            'data': {
                'assignments': assignments,
                'stats': {
                    'total': len(assignments),
                    'configured': configured_count,
                    'unconfigured_required': unconfigured_required,
                    'unconfigured_optional': unconfigured_optional
                }
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_OVERVIEW_ERROR',
                'message': str(e)
            }
        }), 500


@api_v1.route('/admin/lm-routing/unconfigured', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_unconfigured_lms():
    """
    Get all learning methods that require a model but don't have one configured.

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "unconfigured": [
                {
                    "learning_method_id": 0,
                    "lm_name": "Deep Explanation",
                    "recommended_categories": ["chat", "reasoning"]
                }
            ],
            "count": 15
        }
    }
    ```
    """
    try:
        unconfigured = LMModelAssignmentRepository.get_unconfigured_lms()

        result = []
        for row in unconfigured:
            lm_id = row['learning_method_id']
            lm_def = get_method_by_id(lm_id)

            result.append({
                'learning_method_id': lm_id,
                'lm_code': f'LM{str(lm_id).zfill(2)}',
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
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_UNCONFIGURED_ERROR',
                'message': str(e)
            }
        }), 500


@api_v1.route('/admin/lm-routing/requirements', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_lm_requirements():
    """
    Get all learning method requirements.

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "requirements": [
                {
                    "learning_method_id": 0,
                    "required": true,
                    "recommended_categories": ["chat", "reasoning"],
                    "requires_vision": false
                }
            ]
        }
    }
    ```
    """
    try:
        requirements = LMModelRequirementsRepository.get_all_requirements()

        result = []
        for req in requirements:
            lm_id = req['learning_method_id']
            lm_def = get_method_by_id(lm_id)

            result.append({
                'learning_method_id': lm_id,
                'lm_code': f'LM{str(lm_id).zfill(2)}',
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
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_REQUIREMENTS_ERROR',
                'message': str(e)
            }
        }), 500


# ============================================================================
# Single LM Assignment
# ============================================================================

@api_v1.route('/admin/lm-routing/<int:lm_id>', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_lm_assignment(lm_id: int):
    """
    Get model assignment for a specific learning method.

    **URL Parameters:**
    - lm_id: Learning method ID (0-32)

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "learning_method_id": 0,
            "lm_name": "Deep Explanation",
            "assignment": {
                "assignment_id": 1,
                "model_id": 5,
                "model_name": "gpt-4o",
                "provider_name": "openai"
            }
        }
    }
    ```
    """
    try:
        if lm_id < 0 or lm_id > 32:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_LM_ID',
                    'message': f'Learning method ID must be between 0 and 32'
                }
            }), 400

        lm_def = get_method_by_id(lm_id)
        assignment = LMModelAssignmentRepository.get_assignment_for_lm(lm_id, scope='system')
        requirement = LMModelRequirementsRepository.get_requirement(lm_id)

        return jsonify({
            'success': True,
            'data': {
                'learning_method_id': lm_id,
                'lm_code': f'LM{str(lm_id).zfill(2)}',
                'lm_name': lm_def.name if lm_def else f'LM{lm_id}',
                'lm_group': lm_def.group.value if lm_def else None,
                'lm_type': lm_def.method_type.value if lm_def else None,
                'ki_usage': lm_def.ki_usage.value if lm_def else None,
                'requirement': {
                    'required': requirement.get('required', True) if requirement else True,
                    'recommended_categories': requirement.get('recommended_categories', ['chat']) if requirement else ['chat'],
                    'requires_vision': requirement.get('requires_vision', False) if requirement else False
                },
                'assignment': {
                    'assignment_id': assignment.get('assignment_id'),
                    'model_id': assignment.get('model_id'),
                    'model_name': assignment.get('model_name'),
                    'model_display_name': assignment.get('model_display_name'),
                    'model_category': assignment.get('model_category'),
                    'provider_name': assignment.get('provider_name'),
                    'provider_display_name': assignment.get('provider_display_name')
                } if assignment else None,
                'is_configured': assignment is not None
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_ASSIGNMENT_ERROR',
                'message': str(e)
            }
        }), 500


@api_v1.route('/admin/lm-routing/<int:lm_id>', methods=['PUT'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def set_lm_assignment(lm_id: int):
    """
    Set system-level model assignment for a learning method.

    **URL Parameters:**
    - lm_id: Learning method ID (0-32)

    **Request Body:**
    ```json
    {
        "model_id": 5
    }
    ```

    **Response:**
    ```json
    {
        "success": true,
        "data": { ... },
        "message": "Model assigned to LM00 (Deep Explanation)"
    }
    ```
    """
    try:
        if lm_id < 0 or lm_id > 32:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_LM_ID',
                    'message': f'Learning method ID must be between 0 and 32'
                }
            }), 400

        data = request.get_json()
        if not data or 'model_id' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'model_id is required'
                }
            }), 400

        model_id = data['model_id']
        user_id = g.current_user.get('user_id')

        # Create assignment
        assignment = LMModelAssignmentRepository.set_system_assignment(
            learning_method_id=lm_id,
            model_id=model_id,
            created_by=user_id
        )

        if not assignment:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'CREATE_FAILED',
                    'message': 'Failed to create assignment'
                }
            }), 500

        # Get LM name for message
        lm_def = get_method_by_id(lm_id)
        lm_name = lm_def.name if lm_def else f'LM{lm_id}'

        # Audit log
        AuditService.log_action(
            user_id=user_id,
            action='set_lm_model_assignment',
            resource_type='lm_routing',
            resource_id=str(lm_id),
            details={
                'learning_method_id': lm_id,
                'model_id': model_id
            }
        )

        return jsonify({
            'success': True,
            'data': assignment,
            'message': f'Model assigned to LM{str(lm_id).zfill(2)} ({lm_name})'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SET_ASSIGNMENT_ERROR',
                'message': str(e)
            }
        }), 500


@api_v1.route('/admin/lm-routing/<int:lm_id>', methods=['DELETE'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def remove_lm_assignment(lm_id: int):
    """
    Remove system-level model assignment for a learning method.

    **URL Parameters:**
    - lm_id: Learning method ID (0-32)

    **Response:**
    ```json
    {
        "success": true,
        "message": "Assignment removed for LM00"
    }
    ```
    """
    try:
        if lm_id < 0 or lm_id > 32:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_LM_ID',
                    'message': f'Learning method ID must be between 0 and 32'
                }
            }), 400

        # Get current assignment
        assignment = LMModelAssignmentRepository.get_assignment_for_lm(lm_id, scope='system')

        if not assignment:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': f'No assignment found for LM{str(lm_id).zfill(2)}'
                }
            }), 404

        # Remove assignment
        LMModelAssignmentRepository.remove_assignment(assignment['assignment_id'])

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action='remove_lm_model_assignment',
            resource_type='lm_routing',
            resource_id=str(lm_id),
            details={
                'learning_method_id': lm_id,
                'removed_model_id': assignment.get('model_id')
            }
        )

        return jsonify({
            'success': True,
            'message': f'Assignment removed for LM{str(lm_id).zfill(2)}'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'REMOVE_ASSIGNMENT_ERROR',
                'message': str(e)
            }
        }), 500


# ============================================================================
# Bulk Operations
# ============================================================================

@api_v1.route('/admin/lm-routing/bulk', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def bulk_set_lm_assignments():
    """
    Bulk set multiple system-level assignments.

    **Request Body:**
    ```json
    {
        "assignments": [
            { "learning_method_id": 0, "model_id": 5 },
            { "learning_method_id": 1, "model_id": 5 },
            ...
        ]
    }
    ```

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "created": 10,
            "errors": []
        }
    }
    ```
    """
    try:
        data = request.get_json()
        if not data or 'assignments' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'assignments array is required'
                }
            }), 400

        assignments = data['assignments']
        user_id = g.current_user.get('user_id')

        # Validate all assignments first
        for assignment in assignments:
            lm_id = assignment.get('learning_method_id')
            if lm_id is None or lm_id < 0 or lm_id > 32:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'INVALID_LM_ID',
                        'message': f'Invalid learning_method_id: {lm_id}'
                    }
                }), 400

            if 'model_id' not in assignment:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'MISSING_MODEL_ID',
                        'message': f'model_id missing for LM{lm_id}'
                    }
                }), 400

        # Bulk create
        result = LMModelAssignmentRepository.bulk_set_system_assignments(
            assignments=assignments,
            created_by=user_id
        )

        # Audit log
        AuditService.log_action(
            user_id=user_id,
            action='bulk_set_lm_model_assignments',
            resource_type='lm_routing',
            resource_id='bulk',
            details={
                'count': result['created'],
                'errors': len(result['errors'])
            }
        )

        return jsonify({
            'success': True,
            'data': result,
            'message': f'{result["created"]} assignments created'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'BULK_SET_ERROR',
                'message': str(e)
            }
        }), 500


# ============================================================================
# Model Resolution (for runtime use)
# ============================================================================

@api_v1.route('/admin/lm-routing/resolve', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def resolve_lm_model():
    """
    Resolve which model to use for a learning method with context.
    Used for testing the resolution logic.

    **Request Body:**
    ```json
    {
        "learning_method_id": 0,
        "chapter_id": "optional-chapter-uuid",
        "course_id": "optional-course-uuid"
    }
    ```

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "model_id": 5,
            "model_name": "gpt-4o",
            "provider_name": "openai",
            "scope": "system",
            "is_configured": true
        }
    }
    ```
    """
    try:
        data = request.get_json()
        if not data or 'learning_method_id' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'learning_method_id is required'
                }
            }), 400

        lm_id = data['learning_method_id']
        chapter_id = data.get('chapter_id')
        course_id = data.get('course_id')

        result = LMModelAssignmentRepository.resolve_model_for_lm(
            learning_method_id=lm_id,
            chapter_id=chapter_id,
            course_id=course_id
        )

        # Check if model is required
        is_required = LMModelRequirementsRepository.is_model_required(lm_id)

        return jsonify({
            'success': True,
            'data': {
                **result,
                'model_required': is_required,
                'can_generate': result['is_configured'] or not is_required
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'RESOLVE_ERROR',
                'message': str(e)
            }
        }), 500


# ============================================================================
# Auto-Recommend & Auto-Setup
# ============================================================================

@api_v1.route('/admin/lm-routing/recommend/<int:lm_id>', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_recommended_models(lm_id: int):
    """
    Get recommended models for a specific learning method.
    Filters models based on LM requirements (category, vision, context window).

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "learning_method_id": 0,
            "lm_name": "Deep Explanation",
            "requirements": { ... },
            "recommended_models": [
                { "model_id": 5, "model_name": "gpt-4o", "score": 95, "reason": "Best match" }
            ]
        }
    }
    ```
    """
    try:
        if lm_id < 0 or lm_id > 32:
            return jsonify({
                'success': False,
                'error': {'code': 'INVALID_LM_ID', 'message': 'LM ID must be 0-32'}
            }), 400

        lm_def = get_method_by_id(lm_id)
        requirement = LMModelRequirementsRepository.get_requirement(lm_id)

        if not requirement:
            requirement = {
                'recommended_categories': ['chat'],
                'requires_vision': False,
                'min_context_window': None
            }

        # Get all active models with provider info
        models_query = """
            SELECT
                m.model_id,
                m.model_name,
                m.display_name,
                m.category,
                m.context_window,
                m.max_output_tokens,
                m.supports_vision,
                m.supports_functions,
                m.cost_level,
                m.speed,
                m.input_price_per_1k,
                m.output_price_per_1k,
                p.name as provider_name,
                p.display_name as provider_display_name,
                CASE WHEN p.encrypted_api_key IS NOT NULL THEN TRUE ELSE FALSE END as has_api_key
            FROM ai_models m
            LEFT JOIN ai_providers p ON m.provider_id = p.provider_id
            WHERE m.active = TRUE
            ORDER BY m.input_price_per_1k ASC NULLS LAST
        """
        all_models = fetch_all(models_query)

        recommended_categories = requirement.get('recommended_categories', ['chat'])
        requires_vision = requirement.get('requires_vision', False)
        min_context = requirement.get('min_context_window')

        recommended = []
        for model in all_models:
            # Skip models without API key configured
            if not model.get('has_api_key'):
                continue

            score = 0
            reasons = []

            # Category match (40 points)
            model_cat = model.get('category', 'chat')
            if model_cat in recommended_categories:
                score += 40
                reasons.append(f'Kategorie passt ({model_cat})')
            elif model_cat == 'chat':
                score += 20  # Chat is always somewhat suitable
                reasons.append('Chat-Modell (allgemein geeignet)')

            # Vision support (30 points if required)
            if requires_vision:
                if model.get('supports_vision'):
                    score += 30
                    reasons.append('Vision-Support vorhanden')
                else:
                    continue  # Skip if vision required but not supported

            # Context window (20 points)
            if min_context:
                model_context = model.get('context_window') or 0
                if model_context >= min_context:
                    score += 20
                    reasons.append(f'Context Window ausreichend ({model_context:,})')
                else:
                    score -= 10
                    reasons.append(f'Context Window zu klein ({model_context:,})')

            # Cost bonus (10 points for low cost)
            cost_level = model.get('cost_level', 'medium')
            if cost_level in ['free', 'low']:
                score += 10
                reasons.append('Kostengünstig')
            elif cost_level == 'very_high':
                score -= 5

            # Speed bonus (5 points)
            speed = model.get('speed', 'medium')
            if speed in ['very_fast', 'fast']:
                score += 5
                reasons.append('Schnell')

            if score > 0:
                recommended.append({
                    'model_id': model.get('model_id'),
                    'model_name': model.get('model_name'),
                    'display_name': model.get('display_name'),
                    'category': model_cat,
                    'provider_name': model.get('provider_name'),
                    'provider_display_name': model.get('provider_display_name'),
                    'score': score,
                    'reasons': reasons,
                    'cost_level': cost_level,
                    'supports_vision': model.get('supports_vision', False),
                    'context_window': model.get('context_window')
                })

        # Sort by score (highest first)
        recommended.sort(key=lambda x: x['score'], reverse=True)

        return jsonify({
            'success': True,
            'data': {
                'learning_method_id': lm_id,
                'lm_code': f'LM{str(lm_id).zfill(2)}',
                'lm_name': lm_def.name if lm_def else f'LM{lm_id}',
                'requirements': {
                    'recommended_categories': recommended_categories,
                    'requires_vision': requires_vision,
                    'min_context_window': min_context
                },
                'recommended_models': recommended[:10],  # Top 10
                'total_matching': len(recommended)
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f'Error getting recommendations: {e}')
        return jsonify({
            'success': False,
            'error': {'code': 'RECOMMEND_ERROR', 'message': str(e)}
        }), 500


@api_v1.route('/admin/lm-routing/auto-setup', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def auto_setup_lm_models():
    """
    Automatically assign best matching models to all unconfigured learning methods.
    Uses scoring algorithm to pick optimal model per LM.

    **Request Body (optional):**
    ```json
    {
        "only_required": true,       // Only configure required LMs (default: false)
        "prefer_cheap": true,        // Prefer cheaper models (default: true)
        "overwrite_existing": false  // Overwrite existing assignments (default: false)
    }
    ```

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "configured": 15,
            "skipped": 5,
            "failed": 0,
            "assignments": [...]
        }
    }
    ```
    """
    try:
        data = request.get_json() or {}
        only_required = data.get('only_required', False)
        prefer_cheap = data.get('prefer_cheap', True)
        prefer_expensive = data.get('prefer_expensive', False)
        overwrite_existing = data.get('overwrite_existing', False)

        user_id = g.current_user.get('user_id')

        # Get all requirements
        requirements = {
            r['learning_method_id']: r
            for r in LMModelRequirementsRepository.get_all_requirements()
        }

        # Get current assignments
        current_assignments = {
            a['learning_method_id']: a
            for a in LMModelAssignmentRepository.get_system_assignments()
        }

        # Get all active models with API keys
        models_query = """
            SELECT
                m.model_id,
                m.model_name,
                m.display_name,
                m.category,
                m.context_window,
                m.supports_vision,
                m.cost_level,
                m.speed,
                m.input_price_per_1k,
                p.name as provider_name
            FROM ai_models m
            JOIN ai_providers p ON m.provider_id = p.provider_id
            WHERE m.active = TRUE
            AND p.encrypted_api_key IS NOT NULL
            ORDER BY m.input_price_per_1k ASC NULLS LAST
        """
        available_models = fetch_all(models_query)

        if not available_models:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NO_MODELS',
                    'message': 'Keine Modelle mit konfiguriertem API-Key verfügbar'
                }
            }), 400

        configured = 0
        skipped = 0
        failed = 0
        assignments = []

        for lm_id in range(33):  # LM00-LM32
            lm_def = get_method_by_id(lm_id)
            req = requirements.get(lm_id, {})

            # Skip if only_required and this LM is optional
            if only_required and not req.get('required', True):
                skipped += 1
                continue

            # Skip if already configured and not overwriting
            if lm_id in current_assignments and not overwrite_existing:
                skipped += 1
                continue

            # Find best model for this LM
            recommended_cats = req.get('recommended_categories', ['chat'])
            requires_vision = req.get('requires_vision', False)
            min_context = req.get('min_context_window')

            best_model = None
            best_score = -1

            for model in available_models:
                score = 0
                model_cat = model.get('category', 'chat')

                # Category match
                if model_cat in recommended_cats:
                    score += 40
                elif model_cat == 'chat':
                    score += 20

                # Vision requirement
                if requires_vision and not model.get('supports_vision'):
                    continue  # Skip incompatible

                if requires_vision and model.get('supports_vision'):
                    score += 30

                # Context window
                if min_context:
                    model_context = model.get('context_window') or 0
                    if model_context >= min_context:
                        score += 20
                    else:
                        score -= 20

                # Cost preference
                cost = model.get('cost_level', 'medium')
                if prefer_expensive:
                    # Prefer expensive/premium models
                    if cost == 'very_high':
                        score += 20
                    elif cost == 'high':
                        score += 15
                    elif cost == 'free':
                        score -= 10
                    elif cost == 'low':
                        score -= 5
                elif prefer_cheap:
                    # Prefer cheap models
                    if cost == 'free':
                        score += 15
                    elif cost == 'low':
                        score += 10
                    elif cost == 'very_high':
                        score -= 10

                if score > best_score:
                    best_score = score
                    best_model = model

            if best_model:
                try:
                    LMModelAssignmentRepository.set_system_assignment(
                        learning_method_id=lm_id,
                        model_id=best_model['model_id'],
                        created_by=user_id
                    )
                    configured += 1
                    assignments.append({
                        'lm_id': lm_id,
                        'lm_code': f'LM{str(lm_id).zfill(2)}',
                        'lm_name': lm_def.name if lm_def else f'LM{lm_id}',
                        'model_name': best_model['model_name'],
                        'provider': best_model['provider_name'],
                        'score': best_score
                    })
                except Exception as assign_err:
                    current_app.logger.error(f'Failed to assign LM{lm_id}: {assign_err}')
                    failed += 1
            else:
                failed += 1

        # Audit log
        AuditService.log_action(
            user_id=user_id,
            action='auto_setup_lm_models',
            resource_type='lm_routing',
            resource_id='auto',
            details={
                'configured': configured,
                'skipped': skipped,
                'failed': failed,
                'only_required': only_required,
                'prefer_cheap': prefer_cheap,
                'prefer_expensive': prefer_expensive
            }
        )

        return jsonify({
            'success': True,
            'data': {
                'configured': configured,
                'skipped': skipped,
                'failed': failed,
                'assignments': assignments
            },
            'message': f'{configured} Lernmethoden automatisch konfiguriert'
        }), 200

    except Exception as e:
        current_app.logger.error(f'Auto-setup error: {e}')
        return jsonify({
            'success': False,
            'error': {'code': 'AUTO_SETUP_ERROR', 'message': str(e)}
        }), 500
# ============================================================================
# AI-Powered Intelligent Auto-Setup (using gpt-4o)
# ============================================================================

@api_v1.route('/admin/lm-routing/ai-auto-setup', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def ai_auto_setup_lm_models():
    """
    AI-powered intelligent model assignment using gpt-4o.

    Uses OpenAI's gpt-4o to analyze each learning method's requirements
    and intelligently select the best matching model with reasoning.

    This is a one-time operation that provides better results than
    the simple scoring algorithm.
    """
    import json as json_module

    try:
        data = request.get_json() or {}
        ai_model = data.get('model', 'gpt-4o')
        overwrite_existing = data.get('overwrite_existing', False)
        user_id = g.current_user.get('user_id')

        # Get all active models with API keys
        models_query = """
            SELECT
                m.model_id,
                m.model_name,
                m.display_name,
                m.category,
                m.context_window,
                m.max_output_tokens,
                m.supports_vision,
                m.supports_functions,
                m.cost_level,
                m.speed,
                m.input_price_per_1k,
                m.output_price_per_1k,
                p.name as provider_name,
                p.display_name as provider_display_name
            FROM ai_models m
            JOIN ai_providers p ON m.provider_id = p.provider_id
            WHERE m.active = TRUE
            AND p.encrypted_api_key IS NOT NULL
            ORDER BY m.input_price_per_1k ASC NULLS LAST
        """
        available_models = fetch_all(models_query)

        if not available_models:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NO_MODELS',
                    'message': 'Keine Modelle mit konfiguriertem API-Key verfügbar'
                }
            }), 400

        # Get current assignments
        current_assignments = {
            a['learning_method_id']: a
            for a in LMModelAssignmentRepository.get_system_assignments()
        }

        # Build the prompt for gpt-4o
        lm_descriptions = []
        for lm_id in range(33):
            lm_def = get_method_by_id(lm_id)
            if lm_def:
                # Skip if already configured and not overwriting
                if lm_id in current_assignments and not overwrite_existing:
                    continue

                lm_descriptions.append({
                    'lm_id': lm_id,
                    'code': f'LM{str(lm_id).zfill(2)}',
                    'name': lm_def.name,
                    'group': lm_def.group.value,
                    'type': lm_def.method_type.value,
                    'ki_usage': lm_def.ki_usage.value,
                    'description': lm_def.description
                })

        if not lm_descriptions:
            return jsonify({
                'success': True,
                'data': {
                    'configured': 0,
                    'skipped': 33,
                    'message': 'Alle Lernmethoden sind bereits konfiguriert.'
                }
            }), 200

        # Format available models for the prompt
        model_descriptions = []
        for m in available_models:
            model_descriptions.append({
                'model_id': m['model_id'],
                'name': m['model_name'],
                'display_name': m['display_name'],
                'provider': m['provider_name'],
                'category': m['category'],
                'context_window': m['context_window'],
                'supports_vision': m['supports_vision'],
                'supports_functions': m['supports_functions'],
                'cost_level': m['cost_level'],
                'speed': m['speed']
            })

        # Build the AI prompt
        system_prompt = '''Du bist ein KI-Experte für Lernmethoden und AI-Modellauswahl.

Deine Aufgabe: Analysiere jede Lernmethode und wähle das OPTIMALE KI-Modell basierend auf:
1. **KI-Intensität**: intensive Methoden brauchen leistungsstarke Modelle, optional nur einfache
2. **Methodentyp**: explanatory braucht gute Sprachqualität, practice/exam oft strukturierte Outputs
3. **Spezialanforderungen**: Vision für Whiteboard, Code für Coding-Sandbox, Reasoning für komplexe Aufgaben
4. **Kosten-Nutzen**: Günstigere Modelle für einfache Tasks, teurere nur wenn nötig

Wichtige Kategorien:
- "chat": Allgemeine Konversation/Erklärungen
- "reasoning": Komplexes Denken, Problemlösung, Multi-Step-Aufgaben
- "coding": Code-Generierung und Analyse
- "vision": Bildverarbeitung (Whiteboard, Diagramme)

Antworte NUR mit einem validen JSON-Array (keine Markdown, keine Erklärung außerhalb).'''

        lm_json = json_module.dumps(lm_descriptions, indent=2, ensure_ascii=False)
        model_json = json_module.dumps(model_descriptions, indent=2, ensure_ascii=False)

        user_prompt = f'''Analysiere diese {len(lm_descriptions)} Lernmethoden und wähle jeweils das beste verfügbare Modell:

LERNMETHODEN:
{lm_json}

VERFÜGBARE MODELLE:
{model_json}

Antworte mit einem JSON-Array in diesem Format:
[
  {{"lm_id": 0, "model_id": 5, "reasoning": "Kurze Begründung auf Deutsch"}},
  ...
]

Wichtig:
- Wähle für KI-intensive Methoden (intensive) leistungsstarke Modelle
- Wähle für optionale Methoden günstigere Modelle
- Whiteboard (LM08) braucht Vision-Support
- Code-Sandbox (LM09) braucht Coding-Fähigkeiten
- Sokratischer Dialog (LM29) braucht gutes Reasoning
- Nur JSON-Array zurückgeben!'''

        # Call the AI
        from app.services.ai_adapter import AIAdapter, AIProviderError

        try:
            adapter = AIAdapter(provider='openai', model=ai_model)
            response = adapter.send_messages(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )

            ai_response = response['output_text'].strip()
            total_cost = response['cost_eur']

            # Clean up potential markdown formatting
            if ai_response.startswith('```'):
                ai_response = ai_response.split('```')[1]
                if ai_response.startswith('json'):
                    ai_response = ai_response[4:]
            ai_response = ai_response.strip()

            assignments_data = json_module.loads(ai_response)

        except AIProviderError as e:
            current_app.logger.error(f'AI Auto-setup API error: {e}')
            return jsonify({
                'success': False,
                'error': {'code': 'AI_API_ERROR', 'message': f'Fehler beim AI-Aufruf: {str(e)}'}
            }), 500
        except json_module.JSONDecodeError as e:
            current_app.logger.error(f'AI response not valid JSON: {ai_response[:500]}')
            return jsonify({
                'success': False,
                'error': {'code': 'AI_RESPONSE_ERROR', 'message': f'AI-Antwort war kein gültiges JSON: {str(e)}'}
            }), 500

        # Create model_id lookup
        model_id_lookup = {m['model_id']: m for m in available_models}

        # Apply the assignments
        configured = 0
        failed = 0
        result_assignments = []

        for assignment in assignments_data:
            lm_id = assignment.get('lm_id')
            model_id = assignment.get('model_id')
            reasoning = assignment.get('reasoning', '')

            if lm_id is None or model_id is None:
                failed += 1
                continue

            if model_id not in model_id_lookup:
                failed += 1
                continue

            model_info = model_id_lookup[model_id]
            lm_def = get_method_by_id(lm_id)

            try:
                LMModelAssignmentRepository.set_system_assignment(
                    learning_method_id=lm_id,
                    model_id=model_id,
                    created_by=user_id
                )
                configured += 1
                result_assignments.append({
                    'lm_id': lm_id,
                    'lm_code': f'LM{str(lm_id).zfill(2)}',
                    'lm_name': lm_def.name if lm_def else f'LM{lm_id}',
                    'model_id': model_id,
                    'model_name': model_info['model_name'],
                    'provider': model_info['provider_name'],
                    'reasoning': reasoning
                })
            except Exception as assign_err:
                current_app.logger.error(f'Failed to assign LM{lm_id}: {assign_err}')
                failed += 1

        # Audit log
        AuditService.log_action(
            user_id=user_id,
            action='ai_auto_setup_lm_models',
            resource_type='lm_routing',
            resource_id='ai_auto',
            details={
                'configured': configured,
                'failed': failed,
                'ai_model': ai_model,
                'cost_eur': total_cost,
                'overwrite_existing': overwrite_existing
            }
        )

        return jsonify({
            'success': True,
            'data': {
                'configured': configured,
                'failed': failed,
                'assignments': result_assignments,
                'ai_model_used': ai_model,
                'total_cost_eur': round(total_cost, 4)
            },
            'message': f'{configured} Lernmethoden wurden intelligent von {ai_model} konfiguriert'
        }), 200

    except Exception as e:
        current_app.logger.error(f'AI Auto-setup error: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': {'code': 'AI_AUTO_SETUP_ERROR', 'message': str(e)}
        }), 500


# ============================================================================
# Capability Slots System (Multi-Model per LM)
# ============================================================================

from app.services.lm_slot_resolver import get_resolver, get_manager
from app.repositories.lm_slot_repository import (
    CapabilitySlotRepository,
    LMSlotRequirementRepository,
    LMSlotAssignmentRepository
)


@api_v1.route('/admin/lm-routing/slots', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_all_capability_slots():
    """
    Get all available capability slots.

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "slots": [
                {
                    "slot_id": 1,
                    "slot_code": "chat",
                    "display_name": "Chat/Text",
                    "description": "Standard text generation",
                    "required_category": "chat",
                    "icon": "message-square",
                    "sort_order": 10
                },
                ...
            ]
        }
    }
    ```
    """
    try:
        slots = CapabilitySlotRepository.find_all_sorted()

        return jsonify({
            'success': True,
            'data': {
                'slots': slots
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'GET_SLOTS_ERROR', 'message': str(e)}
        }), 500


@api_v1.route('/admin/lm-routing/<int:lm_id>/slots', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_lm_slot_overview(lm_id: int):
    """
    Get complete slot overview for a learning method.

    Shows all slots (required + optional), their current assignments,
    and compatible models for each slot.

    **URL Parameters:**
    - lm_id: Learning method ID (0-32)

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "learning_method_id": 24,
            "lm_name": "Mündliche Erklärung",
            "group": "C",
            "ready": false,
            "required_count": 2,
            "configured_count": 1,
            "slots": [
                {
                    "slot_code": "chat",
                    "slot_display_name": "Chat/Text",
                    "is_required": true,
                    "is_primary": true,
                    "is_configured": true,
                    "model": { "model_id": 1, "model_name": "gpt-4o", ... },
                    "resolved_scope": "system"
                },
                {
                    "slot_code": "stt",
                    "is_required": true,
                    "is_configured": false,
                    "model": null
                },
                ...
            ]
        }
    }
    ```
    """
    try:
        if lm_id < 0 or lm_id > 32:
            return jsonify({
                'success': False,
                'error': {'code': 'INVALID_LM_ID', 'message': 'LM ID must be 0-32'}
            }), 400

        resolver = get_resolver()
        overview = resolver.get_lm_overview(lm_id)

        if not overview:
            return jsonify({
                'success': False,
                'error': {'code': 'LM_NOT_FOUND', 'message': f'LM{lm_id} not found'}
            }), 404

        # Add compatible models for each slot
        manager = get_manager()
        for slot in overview.get('slots', []):
            slot['compatible_models'] = manager.get_compatible_models(slot['slot_code'])

        return jsonify({
            'success': True,
            'data': overview
        }), 200

    except Exception as e:
        current_app.logger.error(f'Error getting LM slot overview: {e}')
        return jsonify({
            'success': False,
            'error': {'code': 'GET_LM_SLOTS_ERROR', 'message': str(e)}
        }), 500


@api_v1.route('/admin/lm-routing/<int:lm_id>/slots/<slot_code>', methods=['PUT'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def assign_slot_model(lm_id: int, slot_code: str):
    """
    Assign a model to a specific slot for a learning method.

    **URL Parameters:**
    - lm_id: Learning method ID (0-32)
    - slot_code: Slot code (chat, stt, tts, vision, realtime, etc.)

    **Request Body:**
    ```json
    {
        "model_id": 5,
        "scope": "system",           // Optional: system, course, chapter
        "scope_reference_id": null   // Optional: course_id or chapter_id
    }
    ```

    **Response:**
    ```json
    {
        "success": true,
        "data": { ... },
        "message": "Model gpt-4o assigned to CHAT slot for LM24"
    }
    ```
    """
    try:
        if lm_id < 0 or lm_id > 32:
            return jsonify({
                'success': False,
                'error': {'code': 'INVALID_LM_ID', 'message': 'LM ID must be 0-32'}
            }), 400

        data = request.get_json()
        if not data or 'model_id' not in data:
            return jsonify({
                'success': False,
                'error': {'code': 'INVALID_REQUEST', 'message': 'model_id is required'}
            }), 400

        model_id = data['model_id']
        scope = data.get('scope', 'system')
        scope_reference_id = data.get('scope_reference_id')
        user_id = g.current_user.get('user_id')

        manager = get_manager()

        try:
            assignment = manager.assign_model(
                learning_method_id=lm_id,
                slot_code=slot_code,
                model_id=model_id,
                scope=scope,
                scope_reference_id=scope_reference_id,
                created_by=user_id
            )
        except ValueError as ve:
            return jsonify({
                'success': False,
                'error': {'code': 'INVALID_SLOT', 'message': str(ve)}
            }), 400

        # Get model name for message
        from app.repositories.ai_models_repository import AIModelsRepository
        model = AIModelsRepository.get_by_id(model_id)
        model_name = model.get('model_name', f'Model {model_id}') if model else f'Model {model_id}'

        lm_def = get_method_by_id(lm_id)
        lm_name = lm_def.name if lm_def else f'LM{lm_id}'

        # Audit log
        AuditService.log_action(
            user_id=user_id,
            action='assign_slot_model',
            resource_type='lm_slot_routing',
            resource_id=f'{lm_id}:{slot_code}',
            details={
                'learning_method_id': lm_id,
                'slot_code': slot_code,
                'model_id': model_id,
                'scope': scope
            }
        )

        return jsonify({
            'success': True,
            'data': assignment,
            'message': f'Model {model_name} assigned to {slot_code.upper()} slot for LM{str(lm_id).zfill(2)} ({lm_name})'
        }), 200

    except Exception as e:
        current_app.logger.error(f'Error assigning slot model: {e}')
        return jsonify({
            'success': False,
            'error': {'code': 'ASSIGN_SLOT_ERROR', 'message': str(e)}
        }), 500


@api_v1.route('/admin/lm-routing/<int:lm_id>/slots/<slot_code>', methods=['DELETE'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def remove_slot_assignment(lm_id: int, slot_code: str):
    """
    Remove a slot assignment for a learning method.

    **URL Parameters:**
    - lm_id: Learning method ID (0-32)
    - slot_code: Slot code

    **Query Parameters:**
    - scope: system, course, or chapter (default: system)
    - scope_reference_id: course_id or chapter_id (for non-system scope)

    **Response:**
    ```json
    {
        "success": true,
        "message": "Assignment removed for CHAT slot on LM24"
    }
    ```
    """
    try:
        if lm_id < 0 or lm_id > 32:
            return jsonify({
                'success': False,
                'error': {'code': 'INVALID_LM_ID', 'message': 'LM ID must be 0-32'}
            }), 400

        scope = request.args.get('scope', 'system')
        scope_reference_id = request.args.get('scope_reference_id')
        user_id = g.current_user.get('user_id')

        manager = get_manager()
        removed = manager.remove_assignment(
            learning_method_id=lm_id,
            slot_code=slot_code,
            scope=scope,
            scope_reference_id=scope_reference_id
        )

        if not removed:
            return jsonify({
                'success': False,
                'error': {'code': 'NOT_FOUND', 'message': f'No assignment found for {slot_code} slot'}
            }), 404

        # Audit log
        AuditService.log_action(
            user_id=user_id,
            action='remove_slot_assignment',
            resource_type='lm_slot_routing',
            resource_id=f'{lm_id}:{slot_code}',
            details={
                'learning_method_id': lm_id,
                'slot_code': slot_code,
                'scope': scope
            }
        )

        return jsonify({
            'success': True,
            'message': f'Assignment removed for {slot_code.upper()} slot on LM{str(lm_id).zfill(2)}'
        }), 200

    except Exception as e:
        current_app.logger.error(f'Error removing slot assignment: {e}')
        return jsonify({
            'success': False,
            'error': {'code': 'REMOVE_SLOT_ERROR', 'message': str(e)}
        }), 500


@api_v1.route('/admin/lm-routing/<int:lm_id>/slots/bulk', methods=['PUT'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def bulk_assign_slots(lm_id: int):
    """
    Bulk assign multiple slots for a learning method.

    **URL Parameters:**
    - lm_id: Learning method ID (0-32)

    **Request Body:**
    ```json
    {
        "assignments": [
            { "slot_code": "chat", "model_id": 1 },
            { "slot_code": "stt", "model_id": 5 },
            { "slot_code": "tts", "model_id": 6 }
        ],
        "scope": "system",
        "scope_reference_id": null
    }
    ```

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "created": 3,
            "assignments": [...]
        }
    }
    ```
    """
    try:
        if lm_id < 0 or lm_id > 32:
            return jsonify({
                'success': False,
                'error': {'code': 'INVALID_LM_ID', 'message': 'LM ID must be 0-32'}
            }), 400

        data = request.get_json()
        if not data or 'assignments' not in data:
            return jsonify({
                'success': False,
                'error': {'code': 'INVALID_REQUEST', 'message': 'assignments array is required'}
            }), 400

        assignments = data['assignments']
        scope = data.get('scope', 'system')
        scope_reference_id = data.get('scope_reference_id')
        user_id = g.current_user.get('user_id')

        manager = get_manager()
        results = manager.bulk_assign(
            learning_method_id=lm_id,
            assignments=assignments,
            scope=scope,
            scope_reference_id=scope_reference_id,
            created_by=user_id
        )

        # Audit log
        AuditService.log_action(
            user_id=user_id,
            action='bulk_assign_slots',
            resource_type='lm_slot_routing',
            resource_id=str(lm_id),
            details={
                'learning_method_id': lm_id,
                'count': len(results),
                'slots': [a.get('slot_code') for a in assignments]
            }
        )

        return jsonify({
            'success': True,
            'data': {
                'created': len(results),
                'assignments': results
            },
            'message': f'{len(results)} slots assigned for LM{str(lm_id).zfill(2)}'
        }), 200

    except Exception as e:
        current_app.logger.error(f'Error bulk assigning slots: {e}')
        return jsonify({
            'success': False,
            'error': {'code': 'BULK_ASSIGN_ERROR', 'message': str(e)}
        }), 500


@api_v1.route('/admin/lm-routing/<int:lm_id>/slots/resolve', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def resolve_lm_slots(lm_id: int):
    """
    Test resolution of all slots for a learning method.

    Useful for testing hierarchical resolution (chapter > course > system).

    **URL Parameters:**
    - lm_id: Learning method ID (0-32)

    **Request Body:**
    ```json
    {
        "chapter_id": "optional-chapter-uuid",
        "course_id": "optional-course-uuid"
    }
    ```

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "learning_method_id": 24,
            "ready": true,
            "slots": {
                "chat": { "model_name": "gpt-4o", "scope": "system", ... },
                "stt": { "model_name": "whisper-1", "scope": "system", ... },
                "tts": null,
                "realtime": null
            }
        }
    }
    ```
    """
    try:
        if lm_id < 0 or lm_id > 32:
            return jsonify({
                'success': False,
                'error': {'code': 'INVALID_LM_ID', 'message': 'LM ID must be 0-32'}
            }), 400

        data = request.get_json() or {}
        chapter_id = data.get('chapter_id')
        course_id = data.get('course_id')

        resolver = get_resolver()
        models = resolver.resolve_lm_models(lm_id, chapter_id, course_id)
        ready_check = resolver.check_lm_ready(lm_id, chapter_id, course_id)

        # Convert ResolvedModel to dict
        slots_dict = {}
        for slot_code, resolved in models.items():
            if resolved:
                slots_dict[slot_code] = {
                    'slot_display_name': resolved.slot_display_name,
                    'is_required': resolved.is_required,
                    'is_primary': resolved.is_primary,
                    'is_configured': resolved.is_configured,
                    'model_id': resolved.model_id,
                    'model_name': resolved.model_name,
                    'model_display_name': resolved.model_display_name,
                    'provider_name': resolved.provider_name,
                    'resolved_scope': resolved.resolved_scope
                }
            else:
                slots_dict[slot_code] = None

        return jsonify({
            'success': True,
            'data': {
                'learning_method_id': lm_id,
                'ready': ready_check['ready'],
                'required_count': ready_check['required_count'],
                'configured_count': ready_check['configured_count'],
                'missing_slots': ready_check['missing_slots'],
                'slots': slots_dict
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f'Error resolving LM slots: {e}')
        return jsonify({
            'success': False,
            'error': {'code': 'RESOLVE_SLOTS_ERROR', 'message': str(e)}
        }), 500


@api_v1.route('/admin/lm-routing/slots/overview', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_all_lm_slots_overview():
    """
    Get overview of all LMs with their slot configurations.

    Used for admin dashboard to show which LMs have all required slots configured.

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "lms": [
                {
                    "learning_method_id": 0,
                    "name": "Deep Explanation",
                    "group": "A",
                    "ready": true,
                    "required_count": 1,
                    "configured_count": 1,
                    "slots": [...]
                },
                ...
            ],
            "stats": {
                "total": 33,
                "ready": 20,
                "not_ready": 13,
                "missing_required": 5
            }
        }
    }
    ```
    """
    try:
        resolver = get_resolver()
        all_overviews = resolver.get_all_lm_overview()

        # Calculate stats
        ready_count = sum(1 for lm in all_overviews if lm.get('ready', False))
        not_ready_count = len(all_overviews) - ready_count

        # Count LMs missing required slots
        missing_required = sum(
            1 for lm in all_overviews
            if lm.get('required_count', 0) > lm.get('configured_count', 0)
        )

        return jsonify({
            'success': True,
            'data': {
                'lms': all_overviews,
                'stats': {
                    'total': len(all_overviews),
                    'ready': ready_count,
                    'not_ready': not_ready_count,
                    'missing_required': missing_required
                }
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f'Error getting slots overview: {e}')
        return jsonify({
            'success': False,
            'error': {'code': 'GET_OVERVIEW_ERROR', 'message': str(e)}
        }), 500


@api_v1.route('/admin/lm-routing/slots/<slot_code>/models', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_compatible_models_for_slot(slot_code: str):
    """
    Get all models compatible with a specific slot.

    Used for model dropdown when assigning a model to a slot.

    **URL Parameters:**
    - slot_code: Slot code (chat, stt, tts, vision, realtime, etc.)

    **Response:**
    ```json
    {
        "success": true,
        "data": {
            "slot_code": "stt",
            "slot_display_name": "Speech-to-Text",
            "compatible_models": [
                {
                    "model_id": 5,
                    "model_name": "whisper-1",
                    "display_name": "Whisper",
                    "provider_name": "openai"
                }
            ]
        }
    }
    ```
    """
    try:
        slot = CapabilitySlotRepository.find_by_code(slot_code)
        if not slot:
            return jsonify({
                'success': False,
                'error': {'code': 'SLOT_NOT_FOUND', 'message': f'Unknown slot: {slot_code}'}
            }), 404

        manager = get_manager()
        models = manager.get_compatible_models(slot_code)

        return jsonify({
            'success': True,
            'data': {
                'slot_code': slot_code,
                'slot_display_name': slot.get('display_name'),
                'required_category': slot.get('required_category'),
                'compatible_models': models
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f'Error getting compatible models: {e}')
        return jsonify({
            'success': False,
            'error': {'code': 'GET_MODELS_ERROR', 'message': str(e)}
        }), 500


@api_v1.route('/admin/lm-routing/slots/apply-preset', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def apply_slot_preset():
    """
    Apply a cost preset to all LM slots.

    Automatically configures all slots for all LMs with models matching the cost preset.

    **Request Body:**
    ```json
    {
        "preset": "cheap" | "medium" | "expensive"
    }
    ```

    **Presets:**
    - cheap: Prefer free/low cost models
    - medium: Prefer medium cost models
    - expensive: Prefer high/very_high cost (premium) models
    """
    try:
        data = request.get_json() or {}
        preset = data.get('preset', 'medium')

        if preset not in ['cheap', 'medium', 'expensive']:
            return jsonify({
                'success': False,
                'error': {'code': 'INVALID_PRESET', 'message': 'Preset must be cheap, medium, or expensive'}
            }), 400

        user_id = g.current_user.get('user_id')
        manager = get_manager()
        resolver = get_resolver()

        # Cost level preferences per preset (for non-chat slots)
        cost_preferences = {
            'cheap': ['free', 'low', 'medium', 'high', 'very_high'],
            'medium': ['medium', 'low', 'high', 'free', 'very_high'],
            'expensive': ['very_high', 'high', 'medium', 'low', 'free']
        }
        preferred_costs = cost_preferences[preset]

        # Chat/Text slots ALWAYS use the best model (GPT-5.1)
        chat_cost_preference = ['very_high', 'high', 'medium', 'low', 'free']

        configured = 0
        skipped = 0
        failed = 0
        assignments = []

        # Get all capability slots
        all_slots = CapabilitySlotRepository.find_all_sorted()

        # Process each LM (0-32)
        for lm_id in range(33):
            # Get this LM's slot requirements
            lm_overview = resolver.get_lm_overview(lm_id)
            if not lm_overview:
                continue

            for slot_info in lm_overview.get('slots', []):
                slot_code = slot_info['slot_code']

                try:
                    # Get compatible models for this slot
                    compatible_models = manager.get_compatible_models(slot_code)
                    if not compatible_models:
                        skipped += 1
                        continue

                    # For chat slot: ALWAYS use best model (GPT-5.1)
                    # For other slots: Use preset-based cost preference
                    active_preference = chat_cost_preference if slot_code == 'chat' else preferred_costs

                    # Sort models by cost preference, then by version (newer first)
                    def get_sort_key(model):
                        cost = model.get('cost_level', 'medium')
                        try:
                            cost_priority = active_preference.index(cost)
                        except ValueError:
                            cost_priority = 999

                        # Secondary sort: prefer newer versions (gpt-5.1 before gpt-5)
                        # Higher version numbers should come first
                        model_name = model.get('model_name', '')
                        version_priority = 0
                        if 'gpt-5.1' in model_name:
                            version_priority = -2  # Highest priority
                        elif 'gpt-5' in model_name:
                            version_priority = -1

                        return (cost_priority, version_priority, model_name)

                    sorted_models = sorted(compatible_models, key=get_sort_key)

                    if sorted_models:
                        best_model = sorted_models[0]

                        # Assign the model
                        manager.assign_model(
                            learning_method_id=lm_id,
                            slot_code=slot_code,
                            model_id=best_model['model_id'],
                            scope='system',
                            created_by=user_id
                        )

                        configured += 1
                        assignments.append({
                            'lm_id': lm_id,
                            'lm_code': f'LM{str(lm_id).zfill(2)}',
                            'slot_code': slot_code,
                            'model_name': best_model.get('model_name'),
                            'cost_level': best_model.get('cost_level', 'medium')
                        })
                    else:
                        skipped += 1

                except Exception as slot_err:
                    current_app.logger.error(f'Failed to assign LM{lm_id}/{slot_code}: {slot_err}')
                    failed += 1

        # Audit log
        AuditService.log_action(
            user_id=user_id,
            action='apply_slot_preset',
            resource_type='lm_slot_routing',
            resource_id=preset,
            details={
                'preset': preset,
                'configured': configured,
                'skipped': skipped,
                'failed': failed
            }
        )

        preset_labels = {'cheap': 'Günstig', 'medium': 'Mittel', 'expensive': 'Premium'}

        return jsonify({
            'success': True,
            'data': {
                'preset': preset,
                'preset_label': preset_labels.get(preset, preset),
                'configured': configured,
                'skipped': skipped,
                'failed': failed,
                'assignments': assignments[:20]  # Limit to first 20 for response size
            },
            'message': f'Preset "{preset_labels.get(preset, preset)}" angewendet: {configured} Slots konfiguriert'
        }), 200

    except Exception as e:
        current_app.logger.error(f'Error applying preset: {e}')
        return jsonify({
            'success': False,
            'error': {'code': 'APPLY_PRESET_ERROR', 'message': str(e)}
        }), 500
