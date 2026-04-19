"""
AP2 Module Sub-Area Metadata Repository.

DDD Layer: Infrastructure. psycopg3, parameterized queries only.

Tabelle: assessments.ap2_module_sub_area_meta
Zweck: Display-Meta (Label, Icon, Sort) für Sub-Area-Heatmaps pro Modul.
"""

from typing import Optional
from uuid import UUID

from app.infrastructure.persistence.database.connection import (
    fetch_all, fetch_one, execute_query,
)


class Ap2ModuleSubAreaRepository:
    """assessments.ap2_module_sub_area_meta."""

    @classmethod
    def find_by_module(cls, module_id: UUID) -> list[dict]:
        rows = fetch_all(
            """
            SELECT module_id, sub_area, label_de, label_en,
                   sort_order, icon, color, description
            FROM assessments.ap2_module_sub_area_meta
            WHERE module_id = %s
            ORDER BY sort_order, sub_area
            """,
            (str(module_id),),
        )
        return [dict(r) for r in (rows or [])]

    @classmethod
    def upsert(
        cls,
        module_id: UUID,
        sub_area: str,
        label_de: str,
        sort_order: int = 0,
        label_en: Optional[str] = None,
        icon: Optional[str] = None,
        color: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        execute_query(
            """
            INSERT INTO assessments.ap2_module_sub_area_meta
                (module_id, sub_area, label_de, label_en,
                 sort_order, icon, color, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (module_id, sub_area) DO UPDATE SET
                label_de = EXCLUDED.label_de,
                label_en = EXCLUDED.label_en,
                sort_order = EXCLUDED.sort_order,
                icon = EXCLUDED.icon,
                color = EXCLUDED.color,
                description = EXCLUDED.description
            """,
            (str(module_id), sub_area, label_de, label_en,
             sort_order, icon, color, description),
        )

    @classmethod
    def delete(cls, module_id: UUID, sub_area: str) -> None:
        execute_query(
            """
            DELETE FROM assessments.ap2_module_sub_area_meta
            WHERE module_id = %s AND sub_area = %s
            """,
            (str(module_id), sub_area),
        )
