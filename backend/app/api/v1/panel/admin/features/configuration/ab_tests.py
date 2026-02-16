"""
Feature Configuration Admin API - A/B Test Management

Admin endpoints for managing A/B tests:
- Create and manage A/B tests
- Assign users to variants deterministically
- Track metrics
- Determine winners and apply results

All endpoints require admin authentication.
"""

from flask import Blueprint, jsonify, request, g
from typing import Dict, Any, Tuple, Optional, Literal
import logging
from datetime import datetime

from app.infrastructure.persistence.database import get_db_connection
from app.infrastructure.persistence.repositories.features.configuration_part2 import FeatureAbTestRepository
from app.application.services.feature_flags.ab_test import FeatureConfigurationAbTestService
from app.application.services.feature_flags.cache import FeatureConfigurationCacheService
from app.infrastructure.utils.exceptions import (
    ValidationError,
    NotFoundError,
    ForbiddenError
)
from app.api.middleware.auth import token_required, admin_required

logger = logging.getLogger(__name__)

bp = Blueprint(
    'admin_feature_ab_test',
    __name__,
    url_prefix='/admin/feature-configuration/ab-tests'
)


# ============================================================================
# A/B TEST MANAGEMENT
# ============================================================================

@bp.route('/tests', methods=['GET'])
@token_required
@admin_required
def list_ab_tests() -> Tuple[Dict[str, Any], int]:
    """
    List all A/B tests.

    Query Parameters:
        - feature_name: Filter by feature
        - status: Filter by status (planned, active, paused, completed)
        - limit: Max results (default 50)
        - offset: Skip N results

    Returns:
        200: List of A/B tests
        401: Unauthorized
        403: Forbidden

    Example:
        GET /api/v1/admin/feature-configuration/ab-tests/tests?status=active
    """
    try:
        limit = min(int(request.args.get('limit', 50)), 500)
        offset = int(request.args.get('offset', 0))

        with get_db_connection() as conn:
            repo = FeatureAbTestRepository()

            filters = {}
            if request.args.get('feature_name'):
                filters['feature_name'] = request.args.get('feature_name')
            if request.args.get('status'):
                filters['status'] = request.args.get('status')

            tests = repo.find_all(filters=filters, limit=limit, offset=offset)
            total = repo.count(filters=filters)

        return jsonify({
            'success': True,
            'data': [t.to_dict() if hasattr(t, 'to_dict') else t for t in tests],
            'meta': {
                'total': total,
                'limit': limit,
                'offset': offset
            }
        }), 200

    except Exception as e:
        logger.error(f"Error listing A/B tests: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'LIST_TESTS_FAILED', 'message': 'Failed to list A/B tests'}
        }), 500


@bp.route('/tests', methods=['POST'])
@token_required
@admin_required
def create_ab_test() -> Tuple[Dict[str, Any], int]:
    """
    Create new A/B test.

    Request Body:
        - feature_name: Feature to test (required)
        - test_name: Human-readable test name (required)
        - variant_a_name: Name for variant A (required)
        - variant_a_percentage: % of users in variant A (required)
        - variant_a_config: Optional config override for variant A
        - variant_b_name: Name for variant B (default: "variant_b")
        - variant_b_percentage: % of users in variant B (auto-calculated)
        - variant_b_config: Optional config override for variant B
        - target_roles: Optional list of target roles
        - target_tiers: Optional list of target tiers
        - metrics_to_track: Optional list of metrics
        - planned_duration_days: Expected test duration (default 14)

    Returns:
        201: Created A/B test
        400: Validation error
        409: Test already exists

    Example:
        POST /api/v1/admin/feature-configuration/ab-tests/tests
        {
            "feature_name": "ai_editor",
            "test_name": "UI Theme Test",
            "variant_a_name": "dark_theme",
            "variant_a_percentage": 50,
            "variant_b_name": "light_theme",
            "variant_b_percentage": 50,
            "metrics_to_track": ["engagement", "completion_rate"]
        }
    """
    try:
        data = request.get_json()

        # Validate required fields
        required = ['feature_name', 'test_name', 'variant_a_name', 'variant_a_percentage']
        missing = [f for f in required if f not in data]
        if missing:
            raise ValidationError(f"Missing required fields: {', '.join(missing)}")

        # Create A/B test
        test = FeatureConfigurationAbTestService.create_ab_test(
            feature_name=data['feature_name'],
            test_name=data['test_name'],
            variant_a_name=data['variant_a_name'],
            variant_a_percentage=int(data['variant_a_percentage']),
            variant_a_config=data.get('variant_a_config'),
            variant_b_name=data.get('variant_b_name'),
            variant_b_percentage=data.get('variant_b_percentage'),
            variant_b_config=data.get('variant_b_config'),
            target_roles=data.get('target_roles'),
            target_tiers=data.get('target_tiers'),
            metrics_to_track=data.get('metrics_to_track'),
            planned_duration_days=data.get('planned_duration_days', 14)
        )

        logger.info(
            f"A/B test created: {data['test_name']}",
            extra={'user_id': g.user_id, 'test_name': data['test_name']}
        )

        return jsonify({
            'success': True,
            'data': test
        }), 201

    except ValidationError as e:
        logger.warning(f"Validation error: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}
        }), 400

    except Exception as e:
        logger.error(f"Error creating A/B test: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'CREATE_TEST_FAILED', 'message': 'Failed to create A/B test'}
        }), 500


@bp.route('/tests/<test_id>', methods=['GET'])
@token_required
@admin_required
def get_ab_test(test_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Get single A/B test.

    Returns:
        200: A/B test data
        404: Test not found

    Example:
        GET /api/v1/admin/feature-configuration/ab-tests/tests/{test_id}
    """
    try:
        with get_db_connection() as conn:
            repo = FeatureAbTestRepository()
            test = repo.find_by_id(int(test_id))

        if not test:
            raise NotFoundError(f"A/B test {test_id} not found")

        return jsonify({
            'success': True,
            'data': test.to_dict() if hasattr(test, 'to_dict') else test
        }), 200

    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'TEST_NOT_FOUND', 'message': str(e)}
        }), 404

    except Exception as e:
        logger.error(f"Error getting A/B test {test_id}: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'GET_TEST_FAILED', 'message': 'Failed to get A/B test'}
        }), 500


@bp.route('/tests/<test_id>/start', methods=['POST'])
@token_required
@admin_required
def start_ab_test(test_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Start A/B test (transition to active).

    Returns:
        200: Updated test
        404: Test not found
        409: Test already started

    Example:
        POST /api/v1/admin/feature-configuration/ab-tests/tests/{test_id}/start
    """
    try:
        test = FeatureConfigurationAbTestService.start_ab_test(int(test_id))

        logger.info(
            f"A/B test started: {test_id}",
            extra={'user_id': g.user_id, 'test_id': test_id}
        )

        return jsonify({
            'success': True,
            'data': test
        }), 200

    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'TEST_NOT_FOUND', 'message': str(e)}
        }), 404

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}
        }), 409

    except Exception as e:
        logger.error(f"Error starting A/B test: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'START_TEST_FAILED', 'message': 'Failed to start A/B test'}
        }), 500


@bp.route('/tests/<test_id>/pause', methods=['POST'])
@token_required
@admin_required
def pause_ab_test(test_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Pause A/B test.

    Request Body (optional):
        - reason: Reason for pausing

    Returns:
        200: Updated test
        404: Test not found

    Example:
        POST /api/v1/admin/feature-configuration/ab-tests/tests/{test_id}/pause
        {"reason": "Insufficient sample size"}
    """
    try:
        data = request.get_json() or {}

        test = FeatureConfigurationAbTestService.pause_ab_test(
            int(test_id),
            reason=data.get('reason')
        )

        logger.info(
            f"A/B test paused: {test_id}",
            extra={'user_id': g.user_id, 'test_id': test_id}
        )

        return jsonify({
            'success': True,
            'data': test
        }), 200

    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'TEST_NOT_FOUND', 'message': str(e)}
        }), 404

    except Exception as e:
        logger.error(f"Error pausing A/B test: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'PAUSE_TEST_FAILED', 'message': 'Failed to pause A/B test'}
        }), 500


@bp.route('/tests/<test_id>/end', methods=['POST'])
@token_required
@admin_required
def end_ab_test(test_id: int) -> Tuple[Dict[str, Any], int]:
    """
    End A/B test and declare winner.

    Request Body:
        - winner: Winning variant ('A' or 'B') (required)
        - reason: Reason for winner selection

    Returns:
        200: Updated test
        400: Validation error
        404: Test not found

    Example:
        POST /api/v1/admin/feature-configuration/ab-tests/tests/{test_id}/end
        {"winner": "A", "reason": "Variant A has higher conversion rate"}
    """
    try:
        data = request.get_json() or {}

        if 'winner' not in data:
            raise ValidationError("Missing required field: winner")

        winner = data['winner']
        if winner not in ['A', 'B']:
            raise ValidationError("Winner must be 'A' or 'B'")

        test = FeatureConfigurationAbTestService.end_ab_test(
            int(test_id),
            winner=winner,
            reason=data.get('reason')
        )

        logger.info(
            f"A/B test ended: {test_id}, winner: {winner}",
            extra={'user_id': g.user_id, 'test_id': test_id, 'winner': winner}
        )

        return jsonify({
            'success': True,
            'data': test
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}
        }), 400

    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'TEST_NOT_FOUND', 'message': str(e)}
        }), 404

    except Exception as e:
        logger.error(f"Error ending A/B test: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'END_TEST_FAILED', 'message': 'Failed to end A/B test'}
        }), 500


@bp.route('/tests/<test_id>/metrics', methods=['GET'])
@token_required
@admin_required
def get_ab_test_metrics(test_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Get A/B test metrics and statistics.

    Returns:
        200: Test metrics
        404: Test not found

    Example:
        GET /api/v1/admin/feature-configuration/ab-tests/tests/{test_id}/metrics
    """
    try:
        metrics = FeatureConfigurationAbTestService.get_ab_test_metrics(int(test_id))

        return jsonify({
            'success': True,
            'data': metrics
        }), 200

    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'TEST_NOT_FOUND', 'message': str(e)}
        }), 404

    except Exception as e:
        logger.error(f"Error getting A/B test metrics: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'METRICS_FAILED', 'message': 'Failed to get A/B test metrics'}
        }), 500


@bp.route('/tests/active', methods=['GET'])
@token_required
@admin_required
def list_active_ab_tests() -> Tuple[Dict[str, Any], int]:
    """
    Get all currently active A/B tests.

    Returns:
        200: List of active tests
        401: Unauthorized
        403: Forbidden

    Example:
        GET /api/v1/admin/feature-configuration/ab-tests/tests/active
    """
    try:
        tests = FeatureConfigurationAbTestService.get_active_tests()

        return jsonify({
            'success': True,
            'data': tests,
            'meta': {
                'total': len(tests)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error listing active A/B tests: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'LIST_ACTIVE_FAILED', 'message': 'Failed to list active tests'}
        }), 500


@bp.route('/check-variant/<user_id>/<feature_name>', methods=['GET'])
@token_required
@admin_required
def check_user_variant(user_id: str, feature_name: str) -> Tuple[Dict[str, Any], int]:
    """
    Check what A/B test variant a user is assigned to.

    Returns:
        200: Variant assignment
        404: No active test for feature

    Example:
        GET /api/v1/admin/feature-configuration/ab-tests/check-variant/{user_id}/{feature_name}
    """
    try:
        variant = FeatureConfigurationAbTestService.get_user_ab_test_variant(
            user_id,
            feature_name
        )

        if not variant:
            return jsonify({
                'success': True,
                'data': {
                    'user_id': user_id,
                    'feature_name': feature_name,
                    'assigned_to_test': False
                }
            }), 200

        return jsonify({
            'success': True,
            'data': variant
        }), 200

    except Exception as e:
        logger.error(f"Error checking user variant: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'CHECK_VARIANT_FAILED', 'message': 'Failed to check user variant'}
        }), 500
