"""
AP2 User Learning Prefs + Item Skill Repositories.

DDD Layer: Infrastructure. Only psycopg3, parameterized queries.

Tabellen:
- assessments.ap2_user_learning_prefs (global pro User)
- assessments.ap2_module_item_skill (pro User pro Item)
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, execute_query,
)
from app.domain.models.ap2 import (
    UserLearningPrefs, ItemSkill,
    RecoveryMode, StuetzradDefault, MasteryStrictness,
    DEFAULT_BASE_TARGET, DEFAULT_MAX_TARGET,
)


# ============================================================
# UserLearningPrefs
# ============================================================

def _row_to_prefs(row: dict) -> UserLearningPrefs:
    return UserLearningPrefs(
        user_id=row['user_id'],
        base_target=row.get('base_target', DEFAULT_BASE_TARGET),
        max_target=row.get('max_target', DEFAULT_MAX_TARGET),
        recovery_mode=RecoveryMode(row.get('recovery_mode', 'plus_two')),
        stuetzrad_default=StuetzradDefault(row.get('stuetzrad_default', 'per_item')),
        mastery_strictness=MasteryStrictness(row.get('mastery_strictness', 'standard')),
        created_at=row.get('created_at'),
        updated_at=row.get('updated_at'),
    )


class Ap2UserPrefsRepository:
    """assessments.ap2_user_learning_prefs."""

    @classmethod
    def find_by_user(cls, user_id: UUID) -> Optional[UserLearningPrefs]:
        row = fetch_one(
            "SELECT * FROM assessments.ap2_user_learning_prefs WHERE user_id = %s",
            (str(user_id),),
        )
        return _row_to_prefs(row) if row else None

    @classmethod
    def get_or_create(cls, user_id: UUID) -> UserLearningPrefs:
        existing = cls.find_by_user(user_id)
        if existing:
            return existing
        row = fetch_one(
            """
            INSERT INTO assessments.ap2_user_learning_prefs (user_id)
            VALUES (%s)
            RETURNING *
            """,
            (str(user_id),),
        )
        return _row_to_prefs(row)

    @classmethod
    def upsert(cls, prefs: UserLearningPrefs) -> UserLearningPrefs:
        row = fetch_one(
            """
            INSERT INTO assessments.ap2_user_learning_prefs
                (user_id, base_target, max_target, recovery_mode,
                 stuetzrad_default, mastery_strictness)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                base_target = EXCLUDED.base_target,
                max_target = EXCLUDED.max_target,
                recovery_mode = EXCLUDED.recovery_mode,
                stuetzrad_default = EXCLUDED.stuetzrad_default,
                mastery_strictness = EXCLUDED.mastery_strictness
            RETURNING *
            """,
            (
                str(prefs.user_id),
                prefs.base_target, prefs.max_target,
                prefs.recovery_mode.value,
                prefs.stuetzrad_default.value,
                prefs.mastery_strictness.value,
            ),
        )
        return _row_to_prefs(row)


# ============================================================
# ItemSkill
# ============================================================

def _row_to_skill(row: dict) -> ItemSkill:
    return ItemSkill(
        user_id=row['user_id'],
        item_id=row['item_id'],
        kopf_serie_count=row.get('kopf_serie_count', 0),
        fail_count=row.get('fail_count', 0),
        effective_target=row.get('effective_target', DEFAULT_BASE_TARGET),
        total_attempts=row.get('total_attempts', 0),
        stuetzrad_uses=row.get('stuetzrad_uses', 0),
        is_mastered=row.get('is_mastered', False),
        mastered_at=row.get('mastered_at'),
        snoozed_until=row.get('snoozed_until'),
        last_attempt_at=row.get('last_attempt_at'),
        last_score_pct=(
            float(row['last_score_pct'])
            if row.get('last_score_pct') is not None else None
        ),
        created_at=row.get('created_at'),
        updated_at=row.get('updated_at'),
    )


class Ap2ItemSkillRepository:
    """assessments.ap2_module_item_skill."""

    @classmethod
    def find(cls, user_id: UUID, item_id: UUID) -> Optional[ItemSkill]:
        row = fetch_one(
            """
            SELECT * FROM assessments.ap2_module_item_skill
            WHERE user_id = %s AND item_id = %s
            """,
            (str(user_id), str(item_id)),
        )
        return _row_to_skill(row) if row else None

    @classmethod
    def get_or_init(
        cls, user_id: UUID, item_id: UUID,
        initial_target: int = DEFAULT_BASE_TARGET,
    ) -> ItemSkill:
        existing = cls.find(user_id, item_id)
        if existing:
            return existing
        row = fetch_one(
            """
            INSERT INTO assessments.ap2_module_item_skill
                (user_id, item_id, effective_target)
            VALUES (%s, %s, %s)
            RETURNING *
            """,
            (str(user_id), str(item_id), initial_target),
        )
        return _row_to_skill(row)

    @classmethod
    def upsert(cls, skill: ItemSkill) -> ItemSkill:
        row = fetch_one(
            """
            INSERT INTO assessments.ap2_module_item_skill
                (user_id, item_id, kopf_serie_count, fail_count,
                 effective_target, total_attempts, stuetzrad_uses,
                 is_mastered, mastered_at, snoozed_until,
                 last_attempt_at, last_score_pct)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id, item_id) DO UPDATE SET
                kopf_serie_count = EXCLUDED.kopf_serie_count,
                fail_count = EXCLUDED.fail_count,
                effective_target = EXCLUDED.effective_target,
                total_attempts = EXCLUDED.total_attempts,
                stuetzrad_uses = EXCLUDED.stuetzrad_uses,
                is_mastered = EXCLUDED.is_mastered,
                mastered_at = EXCLUDED.mastered_at,
                snoozed_until = EXCLUDED.snoozed_until,
                last_attempt_at = EXCLUDED.last_attempt_at,
                last_score_pct = EXCLUDED.last_score_pct
            RETURNING *
            """,
            (
                str(skill.user_id), str(skill.item_id),
                skill.kopf_serie_count, skill.fail_count,
                skill.effective_target, skill.total_attempts,
                skill.stuetzrad_uses, skill.is_mastered,
                skill.mastered_at, skill.snoozed_until,
                skill.last_attempt_at, skill.last_score_pct,
            ),
        )
        return _row_to_skill(row)

    @classmethod
    def find_for_items(
        cls, user_id: UUID, item_ids: list[UUID],
    ) -> dict[UUID, ItemSkill]:
        """Bulk-Load: Dict item_id → ItemSkill für gegebene item_ids."""
        if not item_ids:
            return {}
        ids = [str(i) for i in item_ids]
        rows = fetch_all(
            """
            SELECT * FROM assessments.ap2_module_item_skill
            WHERE user_id = %s AND item_id = ANY(%s::uuid[])
            """,
            (str(user_id), ids),
        )
        return {r['item_id']: _row_to_skill(r) for r in (rows or [])}

    @classmethod
    def count_mastered_for_items(
        cls, user_id: UUID, item_ids: list[UUID],
    ) -> int:
        """Wie viele der gegebenen Items sind für den User gemasterd?"""
        if not item_ids:
            return 0
        ids = [str(i) for i in item_ids]
        row = fetch_one(
            """
            SELECT COUNT(*) AS n FROM assessments.ap2_module_item_skill
            WHERE user_id = %s AND item_id = ANY(%s::uuid[]) AND is_mastered = TRUE
            """,
            (str(user_id), ids),
        )
        return int(row['n']) if row else 0

    @classmethod
    def module_stats(
        cls, user_id: UUID, item_ids: list[UUID],
    ) -> dict:
        """Aggregat für Modul-Dashboard."""
        if not item_ids:
            return {
                'total': 0, 'mastered': 0, 'in_progress': 0,
                'recovery': 0, 'total_attempts': 0, 'stuetzrad_uses': 0,
            }
        ids = [str(i) for i in item_ids]
        row = fetch_one(
            """
            SELECT
                COUNT(*) FILTER (WHERE is_mastered = TRUE) AS mastered,
                COUNT(*) FILTER (WHERE is_mastered = FALSE
                                 AND kopf_serie_count > 0) AS in_progress,
                COUNT(*) FILTER (WHERE is_mastered = FALSE
                                 AND fail_count >= 2) AS recovery,
                COALESCE(SUM(total_attempts), 0) AS total_attempts,
                COALESCE(SUM(stuetzrad_uses), 0) AS stuetzrad_uses
            FROM assessments.ap2_module_item_skill
            WHERE user_id = %s AND item_id = ANY(%s::uuid[])
            """,
            (str(user_id), ids),
        )
        return {
            'total': len(item_ids),
            'mastered': int(row['mastered']) if row else 0,
            'in_progress': int(row['in_progress']) if row else 0,
            'recovery': int(row['recovery']) if row else 0,
            'total_attempts': int(row['total_attempts']) if row else 0,
            'stuetzrad_uses': int(row['stuetzrad_uses']) if row else 0,
        }
