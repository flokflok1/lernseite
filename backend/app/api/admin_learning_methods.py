"""
LernsystemX Admin Learning Method API

Admin-Endpoints für Learning Method Instances (31 aktive Lernmethoden, 6 Gruppen A-F):

- GET    /api/v1/admin/chapters/{chapter_id}/learning-methods
- POST   /api/v1/admin/chapters/{chapter_id}/learning-methods
- GET    /api/v1/admin/learning-methods/{method_id}
- PATCH  /api/v1/admin/learning-methods/{method_id}
- DELETE /api/v1/admin/learning-methods/{method_id}
- GET    /api/v1/admin/learning-method-types - Alle aktiven Lernmethoden-Typen

Phase D3.2 - Technische Integration (aktualisiert)
Referenz: 02_Lernmethoden.md
"""

from flask import request, jsonify, g
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

from app.api import api_v1
from app.extensions import limiter
from app.repositories.learning_method_instance_repository import LearningMethodInstanceRepository
from app.repositories.chapter_repository import ChapterRepository
from app.services.audit_service import AuditService
from app.middleware.auth import token_required, get_current_user
from app.security.permissions import require_permission, Permissions
from app.ki.learning_method_mapping import (
    get_all_methods_as_dict,
    get_method_by_id,
    validate_lm_id,
    get_group_info,
    LEARNING_METHODS
)


# =============================================================================
# Pydantic Models für Request-Validierung
# =============================================================================

class AdminLearningMethodCreateRequest(BaseModel):
    """Request für Erstellen einer Learning Method Instance"""
    method_type: int = Field(..., ge=0, le=32, description="LM-ID (0-32, ohne 5/7)")
    title: str = Field(..., min_length=1, max_length=255)
    instructions: Optional[str] = Field(None, max_length=5000)
    data: Dict[str, Any] = Field(default_factory=dict)
    solution: Optional[Dict[str, Any]] = None
    tier: Optional[str] = Field(None, pattern="^(basic|premium|pro)$")
    duration_minutes: Optional[int] = Field(None, ge=1, le=480)
    difficulty: Optional[str] = Field('medium', pattern="^(easy|medium|hard)$")
    order_index: Optional[int] = Field(0, ge=0)
    published: bool = False

    @validator('method_type')
    def validate_method_type(cls, v):
        if not validate_lm_id(v):
            raise ValueError(f'Ungültige method_type: {v}. LM05 und LM07 sind deaktiviert.')
        return v


class AdminLearningMethodUpdateRequest(BaseModel):
    """Request für Update einer Learning Method Instance"""
    method_type: Optional[int] = Field(None, ge=0, le=32)
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    instructions: Optional[str] = Field(None, max_length=5000)
    data: Optional[Dict[str, Any]] = None
    solution: Optional[Dict[str, Any]] = None
    tier: Optional[str] = Field(None, pattern="^(basic|premium|pro)$")
    duration_minutes: Optional[int] = Field(None, ge=1, le=480)
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    order_index: Optional[int] = Field(None, ge=0)
    published: Optional[bool] = None

    @validator('method_type')
    def validate_method_type(cls, v):
        if v is not None and not validate_lm_id(v):
            raise ValueError(f'Ungültige method_type: {v}. LM05 und LM07 sind deaktiviert.')
        return v


# =============================================================================
# Helper Functions
# =============================================================================

def enrich_with_method_info(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Erweitert eine Learning Method Instance mit Typ-Informationen."""
    if not instance:
        return instance

    method_type = instance.get('method_type')
    if method_type is not None:
        method_def = get_method_by_id(method_type)
        if method_def:
            instance['method_name'] = method_def.name
            instance['method_group'] = method_def.group.value
            instance['method_type_name'] = method_def.method_type.value
            instance['ki_usage'] = method_def.ki_usage.value
            instance['prompt_key'] = method_def.prompt_key
            instance['method_description'] = method_def.description

    return instance


# =============================================================================
# API Endpoints
# =============================================================================

@api_v1.route('/admin/learning-method-types', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_READ)
def admin_get_learning_method_types():
    """
    Gibt alle aktiven Lernmethoden-Typen zurück (31 Methoden, 6 Gruppen A-F).

    Response:
        200: Liste aller Lernmethoden-Typen
        {
            "success": true,
            "types": [
                {
                    "lm_id": 0,
                    "name": "Tiefgehende Erklärung",
                    "group": "A",
                    "method_type": "explanatory",
                    "ki_usage": "intensive",
                    "prompt_key": "deep_explanation",
                    "description": "..."
                },
                ...
            ],
            "total": 31,
            "groups": {
                "A": {"name": "Erklärende Methoden", "count": 5},
                "B": {"name": "Praxis/Übung", "count": 6},
                "C": {"name": "Prüfungsorientiert", "count": 8},
                "D": {"name": "Pro/Premium", "count": 4},
                "E": {"name": "IT-Spezifisch", "count": 4},
                "F": {"name": "Kollaborativ", "count": 4}
            }
        }
    """
    try:
        types = get_all_methods_as_dict()

        # Dynamische Gruppeninfo aus der Mapping-Funktion
        groups = get_group_info()

        return jsonify({
            'success': True,
            'types': types,
            'total': len(types),
            'groups': groups
        }), 200

    except Exception as e:
        logger.error(f"Error getting learning method types: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get learning method types',
            'message': str(e)
        }), 500


@api_v1.route('/admin/chapters/<chapter_id>/learning-methods', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_READ)
def admin_get_chapter_learning_methods(chapter_id: str):
    """
    Gibt alle Learning Method Instances für ein Modul zurück.

    Args:
        chapter_id: UUID des Moduls

    Query Parameters:
        published_only: Nur veröffentlichte Methoden (default: false)

    Response:
        200: Liste der Learning Method Instances
        {
            "success": true,
            "learning_methods": [...],
            "total": 5,
            "chapter_id": "..."
        }
    """
    try:
        published_only = request.args.get('published_only', 'false').lower() == 'true'

        # Hole Learning Methods
        methods = LearningMethodInstanceRepository.find_by_chapter(
            chapter_id,
            published_only=published_only
        )

        # Erweitere mit Typ-Informationen
        enriched_methods = [enrich_with_method_info(m) for m in methods]

        # Statistiken
        stats = LearningMethodInstanceRepository.get_statistics_by_chapter(chapter_id)

        return jsonify({
            'success': True,
            'learning_methods': enriched_methods,
            'total': len(enriched_methods),
            'chapter_id': chapter_id,
            'statistics': stats
        }), 200

    except Exception as e:
        logger.error(f"Error getting learning methods for chapter {chapter_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get learning methods',
            'message': str(e)
        }), 500


@api_v1.route('/admin/chapters/<chapter_id>/learning-methods', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_create_learning_method(chapter_id: str):
    """
    Erstellt eine neue Learning Method Instance für ein Modul.

    Args:
        chapter_id: UUID des Moduls

    Request Body:
        {
            "method_type": 13,  // LM-ID (0-31)
            "title": "Flashcards: Python Basics",
            "instructions": "Optional instructions",
            "data": {
                "cards": [
                    {"front": "Was ist eine Variable?", "back": "Ein benannter Speicherplatz"}
                ]
            },
            "solution": null,
            "tier": "basic",
            "duration_minutes": 15,
            "difficulty": "medium",
            "order_index": 0,
            "published": false
        }

    Response:
        201: Erstellte Learning Method Instance
        400: Validation Error
        403: Forbidden
        404: Module not found
    """
    try:
        # Validiere Module existiert
        chapter = ChapterRepository.find_by_id(chapter_id)
        if not chapter:
            return jsonify({
                'success': False,
                'error': 'Module not found',
                'message': f'Module {chapter_id} existiert nicht'
            }), 404

        # Parse und validiere Request
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        try:
            validated = AdminLearningMethodCreateRequest(**data)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Validation error',
                'message': str(e)
            }), 400

        # Erstelle Learning Method Instance
        create_data = validated.dict(exclude_unset=True)
        create_data['chapter_id'] = chapter_id

        result = LearningMethodInstanceRepository.create(create_data)

        # Erweitere mit Typ-Info
        enriched_result = enrich_with_method_info(result)

        # Audit Log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='learning_method.create',
            resource_type='learning_method',
            resource_id=str(result['method_id']),
            details={
                'chapter_id': chapter_id,
                'method_type': validated.method_type,
                'title': validated.title
            }
        )

        return jsonify({
            'success': True,
            'learning_method': enriched_result,
            'message': 'Learning Method Instance erstellt'
        }), 201

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'message': str(e)
        }), 400

    except Exception as e:
        logger.error(f"Error creating learning method: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to create learning method',
            'message': str(e)
        }), 500


@api_v1.route('/admin/learning-methods/<method_id>', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_READ)
def admin_get_learning_method(method_id: str):
    """
    Gibt eine Learning Method Instance zurück.

    Args:
        method_id: UUID der Learning Method Instance

    Response:
        200: Learning Method Instance
        404: Not found
    """
    try:
        result = LearningMethodInstanceRepository.find_by_id(method_id)

        if not result:
            return jsonify({
                'success': False,
                'error': 'Not found',
                'message': f'Learning Method {method_id} nicht gefunden'
            }), 404

        enriched_result = enrich_with_method_info(result)

        return jsonify({
            'success': True,
            'learning_method': enriched_result
        }), 200

    except Exception as e:
        logger.error(f"Error getting learning method {method_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get learning method',
            'message': str(e)
        }), 500


@api_v1.route('/admin/learning-methods/<method_id>', methods=['PATCH'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_update_learning_method(method_id: str):
    """
    Aktualisiert eine Learning Method Instance.

    Args:
        method_id: UUID der Learning Method Instance

    Request Body:
        Teilweise Updates erlaubt - nur geänderte Felder senden.

    Response:
        200: Aktualisierte Learning Method Instance
        400: Validation Error
        404: Not found
    """
    try:
        # Prüfe ob existiert
        existing = LearningMethodInstanceRepository.find_by_id(method_id)
        if not existing:
            return jsonify({
                'success': False,
                'error': 'Not found',
                'message': f'Learning Method {method_id} nicht gefunden'
            }), 404

        # Parse und validiere Request
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        try:
            validated = AdminLearningMethodUpdateRequest(**data)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Validation error',
                'message': str(e)
            }), 400

        # Update
        update_data = validated.dict(exclude_unset=True, exclude_none=True)
        result = LearningMethodInstanceRepository.update(method_id, update_data)

        enriched_result = enrich_with_method_info(result)

        # Audit Log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='learning_method.update',
            resource_type='learning_method',
            resource_id=method_id,
            details={
                'updated_fields': list(update_data.keys())
            }
        )

        return jsonify({
            'success': True,
            'learning_method': enriched_result,
            'message': 'Learning Method Instance aktualisiert'
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'message': str(e)
        }), 400

    except Exception as e:
        logger.error(f"Error updating learning method {method_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update learning method',
            'message': str(e)
        }), 500


@api_v1.route('/admin/learning-methods/<method_id>', methods=['DELETE'])
@require_permission(Permissions.ADMIN_COURSE_DELETE)
def admin_delete_learning_method(method_id: str):
    """
    Löscht eine Learning Method Instance.

    Args:
        method_id: UUID der Learning Method Instance

    Response:
        200: Erfolgreich gelöscht
        404: Not found
    """
    try:
        # Prüfe ob existiert
        existing = LearningMethodInstanceRepository.find_by_id(method_id)
        if not existing:
            return jsonify({
                'success': False,
                'error': 'Not found',
                'message': f'Learning Method {method_id} nicht gefunden'
            }), 404

        # Lösche
        deleted = LearningMethodInstanceRepository.delete(method_id)

        if deleted:
            # Audit Log
            AuditService.log_action(
                user_id=g.current_user['user_id'],
                action='learning_method.delete',
                resource_type='learning_method',
                resource_id=method_id,
                details={
                    'chapter_id': str(existing.get('chapter_id')),
                    'method_type': existing.get('method_type'),
                    'title': existing.get('title')
                }
            )

            return jsonify({
                'success': True,
                'message': 'Learning Method Instance gelöscht'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Delete failed',
                'message': 'Konnte Learning Method nicht löschen'
            }), 500

    except Exception as e:
        logger.error(f"Error deleting learning method {method_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete learning method',
            'message': str(e)
        }), 500


@api_v1.route('/admin/chapters/<chapter_id>/learning-methods/reorder', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_reorder_learning_methods(chapter_id: str):
    """
    Sortiert Learning Methods in einem Modul neu.

    Args:
        chapter_id: UUID des Moduls

    Request Body:
        {
            "method_ids": ["uuid1", "uuid2", "uuid3"]
        }

    Response:
        200: Erfolgreich neu sortiert
    """
    try:
        data = request.get_json()
        if not data or 'method_ids' not in data:
            return jsonify({
                'success': False,
                'error': 'method_ids required'
            }), 400

        method_ids = data['method_ids']

        if not isinstance(method_ids, list):
            return jsonify({
                'success': False,
                'error': 'method_ids must be a list'
            }), 400

        success = LearningMethodInstanceRepository.reorder(chapter_id, method_ids)

        if success:
            # Audit Log
            AuditService.log_action(
                user_id=g.current_user['user_id'],
                action='learning_method.reorder',
                resource_type='chapter',
                resource_id=chapter_id,
                details={
                    'new_order': method_ids
                }
            )

            return jsonify({
                'success': True,
                'message': 'Learning Methods neu sortiert'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Reorder failed'
            }), 500

    except Exception as e:
        logger.error(f"Error reordering learning methods for chapter {chapter_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to reorder learning methods',
            'message': str(e)
        }), 500


@api_v1.route('/admin/learning-methods/<method_id>/publish', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_publish_learning_method(method_id: str):
    """Veröffentlicht eine Learning Method Instance."""
    try:
        result = LearningMethodInstanceRepository.publish(method_id)

        if not result:
            return jsonify({
                'success': False,
                'error': 'Not found'
            }), 404

        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='learning_method.publish',
            resource_type='learning_method',
            resource_id=method_id
        )

        return jsonify({
            'success': True,
            'learning_method': enrich_with_method_info(result),
            'message': 'Learning Method veröffentlicht'
        }), 200

    except Exception as e:
        logger.error(f"Error publishing learning method {method_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1.route('/admin/learning-methods/<method_id>/unpublish', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_unpublish_learning_method(method_id: str):
    """Zieht die Veröffentlichung einer Learning Method Instance zurück."""
    try:
        result = LearningMethodInstanceRepository.unpublish(method_id)

        if not result:
            return jsonify({
                'success': False,
                'error': 'Not found'
            }), 404

        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='learning_method.unpublish',
            resource_type='learning_method',
            resource_id=method_id
        )

        return jsonify({
            'success': True,
            'learning_method': enrich_with_method_info(result),
            'message': 'Learning Method zurückgezogen'
        }), 200

    except Exception as e:
        logger.error(f"Error unpublishing learning method {method_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
