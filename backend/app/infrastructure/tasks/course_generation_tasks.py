"""
Course Generation Tasks -- Celery background tasks for exam course content.

Orchestrates AI Editor plan execution for all chapters in an exam course.
Tracks progress in Redis for real-time frontend updates.
"""
import json
import logging
from typing import Dict, Any, List

from app.core.bootstrap.extensions import celery, redis_client
from app.infrastructure.persistence.repositories.ai.content_plans import (
    ContentPlanRepository,
)

logger = logging.getLogger(__name__)

PROGRESS_KEY_PREFIX = 'course_generation'
PROGRESS_TTL = 3600  # 1 hour


@celery.task(bind=True, max_retries=1, default_retry_delay=60)
def generate_course_content_task(
    self,
    course_id: str,
    ai_plan_ids: List[str],
    user_id: str,
) -> Dict[str, Any]:
    """Execute AI Editor plans for all chapters in an exam course."""
    total = len(ai_plan_ids)
    completed = 0
    failed = 0

    _update_progress(course_id, total, completed, failed, 'generating')

    for plan_id in ai_plan_ids:
        success = _execute_single_plan(plan_id, user_id)
        if success:
            completed += 1
        else:
            failed += 1
        _update_progress(course_id, total, completed, failed, 'generating')

    status = _determine_final_status(completed, failed)
    _update_progress(course_id, total, completed, failed, status)

    logger.info(
        "Course %s generation finished: %d/%d completed, %d failed (%s)",
        course_id, completed, total, failed, status,
    )

    return {
        'course_id': course_id,
        'total': total,
        'completed': completed,
        'failed': failed,
        'status': status,
    }


def _execute_single_plan(plan_id: str, user_id: str) -> bool:
    """Execute a single AI Editor plan. Returns True on success."""
    from app.application.services.ai.plan.plan_execution import (
        execute_plan_background,
    )

    try:
        plan = ContentPlanRepository.find_by_id(plan_id)
        if not plan:
            logger.error("Plan %s not found, skipping", plan_id)
            return False

        execute_plan_background(plan_id, plan, user_id)
        return True
    except Exception:
        logger.exception("Plan %s execution failed", plan_id)
        return False


def _determine_final_status(completed: int, failed: int) -> str:
    """Determine final status based on completed/failed counts."""
    if failed == 0:
        return 'ready'
    if completed == 0:
        return 'failed'
    return 'partial'


def _update_progress(
    course_id: str,
    total: int,
    completed: int,
    failed: int,
    status: str,
) -> None:
    """Write progress to Redis with TTL."""
    if redis_client is None:
        return
    try:
        key = f'{PROGRESS_KEY_PREFIX}:{course_id}'
        value = json.dumps({
            'total': total,
            'completed': completed,
            'failed': failed,
            'status': status,
        })
        redis_client.setex(key, PROGRESS_TTL, value)
    except Exception:
        logger.warning(
            "Could not update Redis progress for course %s", course_id,
        )


def get_generation_progress(course_id: str) -> Dict[str, Any]:
    """
    Read generation progress from Redis.

    Returns a dict with {total, completed, failed, status}.
    Falls back to a default dict if Redis is unavailable or key is missing.
    """
    default = {
        'total': 0,
        'completed': 0,
        'failed': 0,
        'status': 'unknown',
    }

    if redis_client is None:
        return default

    try:
        key = f'{PROGRESS_KEY_PREFIX}:{course_id}'
        raw = redis_client.get(key)
        if raw is None:
            return default
        return json.loads(raw)
    except Exception:
        logger.warning(
            "Could not read Redis progress for course %s", course_id,
        )
        return default
