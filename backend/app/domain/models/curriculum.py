"""
Curriculum Framework Domain Value Objects

Immutable value objects for curriculum/syllabus structures:
- CurriculumObjective: A single learning objective (leaf node)
- CurriculumPosition: A numbered position containing objectives
- CurriculumSection: A section grouping positions
- CurriculumFramework: Root aggregate for a complete curriculum
"""

from dataclasses import dataclass, field
from typing import Optional

VALID_COMPETENCY_LEVELS = frozenset({'kennen', 'anwenden', 'beherrschen'})
VALID_FRAMEWORK_TYPES = frozenset({
    'ihk_ausbildung', 'hochschule', 'zertifizierung', 'custom',
})


@dataclass(frozen=True)
class CurriculumObjective:
    """A single learning objective within a curriculum position."""

    id: int
    objective_code: str
    description: dict = field(default_factory=dict)
    order_index: int = 0
    competency_level: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'CurriculumObjective':
        competency = data.get('competency_level')
        if competency and competency not in VALID_COMPETENCY_LEVELS:
            competency = None
        return cls(
            id=int(data.get('id', 0)),
            objective_code=(data.get('objective_code') or '').strip(),
            description=data.get('description') or {},
            order_index=int(data.get('order_index', 0)),
            competency_level=competency,
        )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'objective_code': self.objective_code,
            'description': dict(self.description),
            'order_index': self.order_index,
            'competency_level': self.competency_level,
        }


@dataclass(frozen=True)
class CurriculumPosition:
    """A numbered position in a curriculum section, containing objectives."""

    id: int
    position_number: str
    display_name: dict = field(default_factory=dict)
    description: dict = field(default_factory=dict)
    order_index: int = 0
    training_period: Optional[str] = None
    objectives: tuple = ()

    @classmethod
    def from_dict(cls, data: dict) -> 'CurriculumPosition':
        raw_objectives = data.get('objectives') or []
        objectives = tuple(
            CurriculumObjective.from_dict(o) if isinstance(o, dict) else o
            for o in raw_objectives
        )
        return cls(
            id=int(data.get('id', 0)),
            position_number=(data.get('position_number') or '').strip(),
            display_name=data.get('display_name') or {},
            description=data.get('description') or {},
            order_index=int(data.get('order_index', 0)),
            training_period=data.get('training_period'),
            objectives=objectives,
        )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'position_number': self.position_number,
            'display_name': dict(self.display_name),
            'description': dict(self.description),
            'order_index': self.order_index,
            'training_period': self.training_period,
            'objectives': [o.to_dict() for o in self.objectives],
        }


@dataclass(frozen=True)
class CurriculumSection:
    """A section in a curriculum framework, grouping positions."""

    id: int
    section_code: str
    display_name: dict = field(default_factory=dict)
    description: dict = field(default_factory=dict)
    order_index: int = 0
    applies_to: tuple = ()
    positions: tuple = ()

    @classmethod
    def from_dict(cls, data: dict) -> 'CurriculumSection':
        raw_positions = data.get('positions') or []
        positions = tuple(
            CurriculumPosition.from_dict(p) if isinstance(p, dict) else p
            for p in raw_positions
        )
        applies_to = tuple(data.get('applies_to') or [])
        return cls(
            id=int(data.get('id', 0)),
            section_code=(data.get('section_code') or '').strip(),
            display_name=data.get('display_name') or {},
            description=data.get('description') or {},
            order_index=int(data.get('order_index', 0)),
            applies_to=applies_to,
            positions=positions,
        )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'section_code': self.section_code,
            'display_name': dict(self.display_name),
            'description': dict(self.description),
            'order_index': self.order_index,
            'applies_to': list(self.applies_to),
            'positions': [p.to_dict() for p in self.positions],
        }


@dataclass(frozen=True)
class CurriculumFramework:
    """Root aggregate for a complete curriculum/syllabus framework."""

    VALID_TYPES = VALID_FRAMEWORK_TYPES

    id: int
    name: str
    framework_type: str = 'custom'
    source_document: Optional[str] = None
    version: Optional[str] = None
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    sections: tuple = ()

    @classmethod
    def from_dict(cls, data: dict) -> 'CurriculumFramework':
        framework_type = data.get('framework_type', 'custom')
        if framework_type not in VALID_FRAMEWORK_TYPES:
            framework_type = 'custom'
        raw_sections = data.get('sections') or []
        sections = tuple(
            CurriculumSection.from_dict(s) if isinstance(s, dict) else s
            for s in raw_sections
        )
        return cls(
            id=int(data.get('id', 0)),
            name=(data.get('name') or '').strip(),
            framework_type=framework_type,
            source_document=data.get('source_document'),
            version=data.get('version'),
            valid_from=data.get('valid_from'),
            valid_until=data.get('valid_until'),
            metadata=data.get('metadata') or {},
            sections=sections,
        )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'framework_type': self.framework_type,
            'source_document': self.source_document,
            'version': self.version,
            'valid_from': self.valid_from,
            'valid_until': self.valid_until,
            'metadata': dict(self.metadata),
            'sections': [s.to_dict() for s in self.sections],
        }

    def to_prompt_context(self, language: str = 'de') -> dict:
        """Return a flat dict suitable for AI prompt template variables."""
        section_names = []
        total_positions = 0
        total_objectives = 0
        for section in self.sections:
            name = section.display_name.get(language) or \
                section.display_name.get('de', section.section_code)
            section_names.append(name)
            total_positions += len(section.positions)
            for position in section.positions:
                total_objectives += len(position.objectives)

        return {
            'curriculum_name': self.name,
            'framework_type': self.framework_type,
            'section_count': len(self.sections),
            'section_names_csv': ', '.join(section_names),
            'total_positions': total_positions,
            'total_objectives': total_objectives,
            'has_curriculum': True,
        }
