"""
Domain Value Objects for AI Content Plan Wizard.

Immutable dataclasses representing plan data at domain boundaries.
Used by PlanGeneratorPort and PlanWizardService for type safety.
"""

from __future__ import annotations

from dataclasses import dataclass, field

VALID_DIFFICULTIES = frozenset({'beginner', 'intermediate', 'advanced', 'expert'})
VALID_CHAT_ROLES = frozenset({'user', 'assistant'})


@dataclass(frozen=True)
class CourseMeta:
    """Phase 1 output: course definition metadata."""

    title: str
    description: str
    target_audience: str
    difficulty: str
    language: str = 'de'
    subtitle: str = ''
    prerequisites: tuple[str, ...] = ()
    estimated_duration_hours: int = 0
    tags: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, data: dict) -> CourseMeta:
        title = data.get('title', '').strip()
        if not title:
            raise ValueError('CourseMeta: title must not be empty')
        difficulty = data.get('difficulty', '')
        if difficulty not in VALID_DIFFICULTIES:
            raise ValueError(
                f'CourseMeta: difficulty must be one of {sorted(VALID_DIFFICULTIES)}, got {difficulty!r}'
            )
        return cls(
            title=title,
            description=data.get('description', ''),
            target_audience=data.get('target_audience', ''),
            difficulty=difficulty,
            language=data.get('language', 'de'),
            subtitle=data.get('subtitle', ''),
            prerequisites=tuple(data.get('prerequisites') or []),
            estimated_duration_hours=int(data.get('estimated_duration_hours', 0)),
            tags=tuple(data.get('tags') or []),
        )

    def to_dict(self) -> dict:
        return {
            'title': self.title,
            'description': self.description,
            'target_audience': self.target_audience,
            'difficulty': self.difficulty,
            'language': self.language,
            'subtitle': self.subtitle,
            'prerequisites': list(self.prerequisites),
            'estimated_duration_hours': self.estimated_duration_hours,
            'tags': list(self.tags),
        }


@dataclass(frozen=True)
class ChapterDraft:
    """Phase 2 output: a single chapter in the course structure."""

    id: str
    title: str
    description: str
    order: int
    estimated_lessons: int = 0
    learning_goals: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, data: dict) -> ChapterDraft:
        order = int(data.get('order', 0))
        if order < 1:
            raise ValueError(f'ChapterDraft: order must be >= 1, got {order}')
        return cls(
            id=data.get('id', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            order=order,
            estimated_lessons=int(data.get('estimated_lessons', 0)),
            learning_goals=tuple(data.get('learning_goals') or []),
        )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'order': self.order,
            'estimated_lessons': self.estimated_lessons,
            'learning_goals': list(self.learning_goals),
        }


@dataclass(frozen=True)
class PlanChatMessage:
    """A single chat message in plan refinement history."""

    role: str
    content: str
    timestamp: str = ''

    @classmethod
    def from_dict(cls, data: dict) -> PlanChatMessage:
        role = data.get('role', '')
        if role not in VALID_CHAT_ROLES:
            raise ValueError(
                f'PlanChatMessage: role must be one of {sorted(VALID_CHAT_ROLES)}, got {role!r}'
            )
        return cls(
            role=role,
            content=data.get('content', ''),
            timestamp=data.get('timestamp', ''),
        )

    def to_dict(self) -> dict:
        return {'role': self.role, 'content': self.content, 'timestamp': self.timestamp}


@dataclass
class PlanData:
    """Container for the full plan state across all phases.

    Not frozen -- mutable container that holds immutable value objects.
    Phases stay as dicts (complex nested structure, low validation value).
    """

    course_meta: CourseMeta | None = None
    chapters: list[ChapterDraft] = field(default_factory=list)
    phases: list[dict] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> PlanData:
        course_meta_raw = data.get('course_meta')
        course_meta = CourseMeta.from_dict(course_meta_raw) if course_meta_raw else None

        chapters_raw = data.get('chapters') or []
        chapters = [ChapterDraft.from_dict(ch) for ch in chapters_raw]

        phases = data.get('phases') or []
        return cls(course_meta=course_meta, chapters=chapters, phases=phases)

    def to_dict(self) -> dict:
        return {
            'course_meta': self.course_meta.to_dict() if self.course_meta else {},
            'chapters': [ch.to_dict() for ch in self.chapters],
            'phases': self.phases,
        }
