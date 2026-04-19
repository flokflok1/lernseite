"""
AP2 Module + Module Progress Repositories.

DDD Layer: Infrastructure. Only psycopg3, parameterized queries.

Tabellen:
- assessments.ap2_modules         — Lehreinheiten (Diagramm-Module)
- assessments.ap2_module_items    — Verknüpfung Module ↔ Aufgaben (Pool)
- assessments.ap2_module_progress — User-spezifischer Fortschritt
- assessments.ap2_module_attempt_log — Audit-Trail
"""

import json
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, execute_query
)
from app.domain.models.ap2 import (
    Module, ModuleProgress, ModuleStatus, AttemptPhase, AttemptSource,
    ModuleAttemptLog,
)


# ============================================================
# Mapping helpers
# ============================================================

def _row_to_module(row: dict) -> Module:
    raw_pre = row.get('prerequisite_slugs') or []
    if isinstance(raw_pre, str):
        raw_pre = json.loads(raw_pre)
    return Module(
        module_id=row['module_id'],
        slug=row['slug'],
        name_de=row['name_de'],
        name_en=row.get('name_en'),
        description=row.get('description'),
        theory_markdown=row.get('theory_markdown'),
        estimated_min=row.get('estimated_min', 12),
        difficulty=row.get('difficulty', 3),
        sort_order=row.get('sort_order', 0),
        prerequisite_slugs=list(raw_pre),
        is_active=row.get('is_active', True),
        created_at=row.get('created_at'),
        updated_at=row.get('updated_at'),
    )


def _row_to_progress(row: dict) -> ModuleProgress:
    used = row.get('used_item_ids') or []
    if isinstance(used, str):
        used = json.loads(used)
    return ModuleProgress(
        progress_id=row['progress_id'],
        user_id=row['user_id'],
        module_id=row['module_id'],
        status=ModuleStatus(row['status']),
        streak_count=row.get('streak_count', 0),
        total_attempts=row.get('total_attempts', 0),
        passed_attempts=row.get('passed_attempts', 0),
        cooldown_until=row.get('cooldown_until'),
        same_day_recall_due_at=row.get('same_day_recall_due_at'),
        same_day_recall_passed=row.get('same_day_recall_passed'),
        mastered_at=row.get('mastered_at'),
        spotcheck_stage=row.get('spotcheck_stage', 0),
        next_spotcheck_at=row.get('next_spotcheck_at'),
        last_spotcheck_at=row.get('last_spotcheck_at'),
        last_spotcheck_score=(
            float(row['last_spotcheck_score'])
            if row.get('last_spotcheck_score') is not None else None
        ),
        used_item_ids=[UUID(str(u)) if not isinstance(u, UUID) else u for u in used],
        created_at=row.get('created_at'),
        updated_at=row.get('updated_at'),
    )


# ============================================================
# Ap2ModuleRepository
# ============================================================

class Ap2ModuleRepository:
    """Repository für assessments.ap2_modules."""

    @classmethod
    def find_all_active(cls) -> list[Module]:
        rows = fetch_all(
            """
            SELECT * FROM assessments.ap2_modules
            WHERE is_active = TRUE
            ORDER BY sort_order, name_de
            """
        )
        return [_row_to_module(r) for r in (rows or [])]

    @classmethod
    def find_by_id(cls, module_id: UUID) -> Optional[Module]:
        row = fetch_one(
            "SELECT * FROM assessments.ap2_modules WHERE module_id = %s",
            (str(module_id),),
        )
        return _row_to_module(row) if row else None

    @classmethod
    def find_by_slug(cls, slug: str) -> Optional[Module]:
        row = fetch_one(
            "SELECT * FROM assessments.ap2_modules WHERE slug = %s",
            (slug,),
        )
        return _row_to_module(row) if row else None

    @classmethod
    def get_pool_item_ids(cls, module_id: UUID,
                          use_in: str = 'mastery') -> list[UUID]:
        """Liefert Item-IDs aus dem Pool. use_in: 'mastery'|'spotcheck'|'both'."""
        rows = fetch_all(
            """
            SELECT item_id FROM assessments.ap2_module_items
            WHERE module_id = %s
              AND (use_in = %s OR use_in = 'both')
            ORDER BY pool_tier, sort_order
            """,
            (str(module_id), use_in),
        )
        return [r['item_id'] for r in (rows or [])]


# ============================================================
# Ap2ModuleProgressRepository
# ============================================================

class Ap2ModuleProgressRepository:
    """Repository für assessments.ap2_module_progress."""

    @classmethod
    def find_by_user_module(
        cls, user_id: UUID, module_id: UUID
    ) -> Optional[ModuleProgress]:
        row = fetch_one(
            """
            SELECT * FROM assessments.ap2_module_progress
            WHERE user_id = %s AND module_id = %s
            """,
            (str(user_id), str(module_id)),
        )
        return _row_to_progress(row) if row else None

    @classmethod
    def find_all_for_user(cls, user_id: UUID) -> list[ModuleProgress]:
        rows = fetch_all(
            """
            SELECT * FROM assessments.ap2_module_progress
            WHERE user_id = %s
            ORDER BY updated_at DESC
            """,
            (str(user_id),),
        )
        return [_row_to_progress(r) for r in (rows or [])]

    @classmethod
    def find_due_recalls(cls) -> list[ModuleProgress]:
        """Same-Day-Recalls die jetzt fällig sind (für Bot-Pings)."""
        rows = fetch_all(
            """
            SELECT * FROM assessments.ap2_module_progress
            WHERE status = 'pending_recall'
              AND same_day_recall_due_at IS NOT NULL
              AND same_day_recall_due_at <= NOW()
            """
        )
        return [_row_to_progress(r) for r in (rows or [])]

    @classmethod
    def find_due_spotchecks(cls, user_id: Optional[UUID] = None) -> list[ModuleProgress]:
        """Fällige Spot-Checks. Optional pro User."""
        if user_id:
            rows = fetch_all(
                """
                SELECT * FROM assessments.ap2_module_progress
                WHERE status = 'mastered'
                  AND user_id = %s
                  AND next_spotcheck_at IS NOT NULL
                  AND next_spotcheck_at <= NOW()
                """,
                (str(user_id),),
            )
        else:
            rows = fetch_all(
                """
                SELECT * FROM assessments.ap2_module_progress
                WHERE status = 'mastered'
                  AND next_spotcheck_at IS NOT NULL
                  AND next_spotcheck_at <= NOW()
                """
            )
        return [_row_to_progress(r) for r in (rows or [])]

    @classmethod
    def upsert(cls, progress: ModuleProgress) -> ModuleProgress:
        """Insert oder Update — primary key ist (user_id, module_id) UNIQUE."""
        used_json = json.dumps([str(u) for u in progress.used_item_ids])
        existing = cls.find_by_user_module(progress.user_id, progress.module_id)
        if existing is None:
            row = fetch_one(
                """
                INSERT INTO assessments.ap2_module_progress
                    (user_id, module_id, status, streak_count, total_attempts,
                     passed_attempts, cooldown_until, same_day_recall_due_at,
                     same_day_recall_passed, mastered_at, spotcheck_stage,
                     next_spotcheck_at, last_spotcheck_at, last_spotcheck_score,
                     used_item_ids)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                RETURNING *
                """,
                (
                    str(progress.user_id), str(progress.module_id),
                    progress.status.value, progress.streak_count,
                    progress.total_attempts, progress.passed_attempts,
                    progress.cooldown_until, progress.same_day_recall_due_at,
                    progress.same_day_recall_passed, progress.mastered_at,
                    progress.spotcheck_stage, progress.next_spotcheck_at,
                    progress.last_spotcheck_at, progress.last_spotcheck_score,
                    used_json,
                ),
            )
        else:
            row = fetch_one(
                """
                UPDATE assessments.ap2_module_progress
                SET status = %s, streak_count = %s, total_attempts = %s,
                    passed_attempts = %s, cooldown_until = %s,
                    same_day_recall_due_at = %s, same_day_recall_passed = %s,
                    mastered_at = %s, spotcheck_stage = %s,
                    next_spotcheck_at = %s, last_spotcheck_at = %s,
                    last_spotcheck_score = %s, used_item_ids = %s::jsonb
                WHERE user_id = %s AND module_id = %s
                RETURNING *
                """,
                (
                    progress.status.value, progress.streak_count,
                    progress.total_attempts, progress.passed_attempts,
                    progress.cooldown_until, progress.same_day_recall_due_at,
                    progress.same_day_recall_passed, progress.mastered_at,
                    progress.spotcheck_stage, progress.next_spotcheck_at,
                    progress.last_spotcheck_at, progress.last_spotcheck_score,
                    used_json,
                    str(progress.user_id), str(progress.module_id),
                ),
            )
        return _row_to_progress(row)

    @classmethod
    def reset_used_items(cls, user_id: UUID, module_id: UUID) -> None:
        """Leert die used_item_ids — z.B. nach Mastery für nächste Session."""
        execute_query(
            """
            UPDATE assessments.ap2_module_progress
            SET used_item_ids = '[]'::jsonb
            WHERE user_id = %s AND module_id = %s
            """,
            (str(user_id), str(module_id)),
        )

    @classmethod
    def log_attempt(cls, log: ModuleAttemptLog) -> UUID:
        """Speichert einen Versuch im Audit-Log."""
        feedback_json = json.dumps(log.feedback) if log.feedback else None
        row = fetch_one(
            """
            INSERT INTO assessments.ap2_module_attempt_log
                (user_id, module_id, item_id, attempt_phase, source,
                 user_answer, score_pct, passed, feedback)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            RETURNING attempt_log_id
            """,
            (
                str(log.user_id), str(log.module_id), str(log.item_id),
                log.attempt_phase.value, log.source.value,
                log.user_answer, log.score_pct, log.passed, feedback_json,
            ),
        )
        return row['attempt_log_id']
