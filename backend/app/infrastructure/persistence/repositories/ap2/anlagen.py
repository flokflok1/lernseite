"""
AP2 Anlage Repository — Beschriftbare Prüfungs-Appendices.

DDD Layer: Infrastructure. Only psycopg3, parameterized queries.
"""

import json
from typing import Optional
from uuid import UUID

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, insert_returning, update_returning,
)
from app.domain.models.ap2 import Anlage, Hotspot, AnlageType, HotspotType


def _hotspots_from_json(raw) -> list[Hotspot]:
    """JSONB hotspots[] → list[Hotspot]."""
    if not raw:
        return []
    data = raw if isinstance(raw, list) else json.loads(raw)
    out: list[Hotspot] = []
    for h in data:
        out.append(Hotspot(
            hotspot_id=h['hotspot_id'],
            x=h['x'], y=h['y'],
            width=h.get('width', 100),
            height=h.get('height', 30),
            hotspot_type=HotspotType(h['hotspot_type']),
            correct_answers=h.get('correct_answers', []),
            points=float(h.get('points', 1.0)),
            tolerance=h.get('tolerance', 'case-insensitive'),
            placeholder=h.get('placeholder'),
            hint=h.get('hint'),
            dropdown_options=h.get('dropdown_options', []),
        ))
    return out


def _hotspots_to_json(hotspots: list[Hotspot]) -> str:
    """list[Hotspot] → JSON string for JSONB column."""
    return json.dumps([{
        'hotspot_id': h.hotspot_id,
        'x': h.x, 'y': h.y, 'width': h.width, 'height': h.height,
        'hotspot_type': h.hotspot_type.value,
        'correct_answers': h.correct_answers,
        'points': h.points, 'tolerance': h.tolerance,
        'placeholder': h.placeholder, 'hint': h.hint,
        'dropdown_options': h.dropdown_options,
    } for h in hotspots])


def _row_to_anlage(row: dict) -> Anlage:
    return Anlage(
        anlage_id=row['anlage_id'],
        slug=row['slug'],
        title=row['title'],
        anlage_type=AnlageType(row['anlage_type']),
        hotspots=_hotspots_from_json(row.get('hotspots')),
        source_exam=row.get('source_exam'),
        anlage_number=row.get('anlage_number'),
        image_url=row.get('image_url'),
        image_width=row.get('image_width'),
        image_height=row.get('image_height'),
        svg_markup=row.get('svg_markup'),
        description=row.get('description'),
        footnote=row.get('footnote'),
        created_at=row.get('created_at'),
        updated_at=row.get('updated_at'),
    )


class Ap2AnlageRepository:
    """Repository für assessments.ap2_anlagen."""

    @classmethod
    def find_by_id(cls, anlage_id: UUID) -> Optional[Anlage]:
        row = fetch_one(
            "SELECT * FROM assessments.ap2_anlagen WHERE anlage_id = %s",
            (str(anlage_id),),
        )
        return _row_to_anlage(row) if row else None

    @classmethod
    def find_by_slug(cls, slug: str) -> Optional[Anlage]:
        row = fetch_one(
            "SELECT * FROM assessments.ap2_anlagen WHERE slug = %s",
            (slug,),
        )
        return _row_to_anlage(row) if row else None

    @classmethod
    def find_all(cls) -> list[Anlage]:
        rows = fetch_all(
            "SELECT * FROM assessments.ap2_anlagen ORDER BY source_exam, anlage_number"
        )
        return [_row_to_anlage(r) for r in (rows or [])]

    @classmethod
    def find_by_source_exam(cls, source_exam: str) -> list[Anlage]:
        rows = fetch_all(
            """
            SELECT * FROM assessments.ap2_anlagen
            WHERE source_exam = %s ORDER BY anlage_number
            """,
            (source_exam,),
        )
        return [_row_to_anlage(r) for r in (rows or [])]

    @classmethod
    def create(cls, anlage: Anlage) -> Anlage:
        row = insert_returning('assessments.ap2_anlagen', {
            'slug': anlage.slug,
            'title': anlage.title,
            'anlage_type': anlage.anlage_type.value,
            'source_exam': anlage.source_exam,
            'anlage_number': anlage.anlage_number,
            'image_url': anlage.image_url,
            'image_width': anlage.image_width,
            'image_height': anlage.image_height,
            'svg_markup': anlage.svg_markup,
            'hotspots': _hotspots_to_json(anlage.hotspots),
            'description': anlage.description,
            'footnote': anlage.footnote,
        })
        return _row_to_anlage(row)

    @classmethod
    def update_hotspots(cls, anlage_id: UUID, hotspots: list[Hotspot]) -> Optional[Anlage]:
        row = update_returning(
            'assessments.ap2_anlagen',
            {'hotspots': _hotspots_to_json(hotspots)},
            'anlage_id = %s',
            (str(anlage_id),),
        )
        return _row_to_anlage(row) if row else None
