"""
Exam Course Plan — Domain Value Objects.

Describes the structure of an auto-generated IHK exam course
before it's persisted to the database.
"""
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def parse_label(value: Any) -> Dict:
    """Parse topic_label to dict, handling both str (JSON) and dict inputs.

    Used by service and builder layers to normalize label data from DB
    or taxonomy lookups.
    """
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    return {}


@dataclass(frozen=True)
class LMMapping:
    """Maps a question_type to a target learning method."""
    question_type: str
    target_lm_type: int
    transform_fn: str


@dataclass(frozen=True)
class ChapterPlan:
    """Plan for a single chapter (= one topic).

    When taxonomy data is available, parent_topic / parent_label /
    child_topics carry the hierarchy information.  All three are
    optional so the dataclass stays backward-compatible with flat
    (non-taxonomy) grouping.
    """
    topic: str
    question_ids: List[str]
    lm_types: List[int]
    point_weight: float
    question_count: int
    parent_topic: Optional[str] = None
    parent_label: Optional[Dict[str, str]] = None
    child_topics: Optional[List[str]] = None
    # Curriculum integration
    curriculum_position_id: Optional[int] = None
    curriculum_position_code: Optional[str] = None
    objectives_total: int = 0
    objectives_with_questions: int = 0
    objectives_ai_only: int = 0
    coverage_pct: float = 0.0              # 0-100 per-position objective coverage
    coverage_source: Optional[str] = None  # "exam_questions" | "ai_generated" | "mixed"
    # Exam relevance (frequency-based + trend)
    relevance_score: float = 0.0          # year-weighted point score
    exam_appearance_rate: float = 0.0     # 0.0-1.0 how often in exams
    relevance_trend: Optional[str] = None  # "rising" | "stable" | "declining"
    # Intelligence scoring (prognosis + user weakness)
    prognosis_probability: float = 0.0    # 0.0-1.0 predicted exam appearance
    prognosis_confidence: Optional[str] = None  # "low" | "medium" | "high"
    user_proficiency: Optional[float] = None    # 0-100 (None = no user data)
    user_severity: Optional[str] = None         # "critical" | "moderate" | "minor" | "none"
    intelligence_score: float = 0.0       # combined priority score


@dataclass(frozen=True)
class ExamCoursePlan:
    """Complete plan for an auto-generated exam course."""
    title: str
    exam_type: str
    region: str
    region_display_name: str = ''
    curriculum_framework_id: Optional[int] = None
    sort_mode: str = 'relevance'
    chapters: List[ChapterPlan] = field(default_factory=list)
    simulation_exam_ids: List[str] = field(default_factory=list)

    @property
    def total_questions(self) -> int:
        return sum(ch.question_count for ch in self.chapters)

    @property
    def total_points(self) -> float:
        return sum(ch.point_weight for ch in self.chapters)

    def to_dict(self) -> dict:
        return {
            'title': self.title,
            'exam_type': self.exam_type,
            'region': self.region,
            'region_display_name': self.region_display_name,
            'curriculum_framework_id': self.curriculum_framework_id,
            'sort_mode': self.sort_mode,
            'total_questions': self.total_questions,
            'total_points': self.total_points,
            'chapters': [
                {
                    'topic': ch.topic,
                    'question_count': ch.question_count,
                    'lm_types': ch.lm_types,
                    'point_weight': ch.point_weight,
                    'parent_topic': ch.parent_topic,
                    'parent_label': ch.parent_label,
                    'child_topics': ch.child_topics,
                    'curriculum_position_id': ch.curriculum_position_id,
                    'curriculum_position_code': ch.curriculum_position_code,
                    'objectives_total': ch.objectives_total,
                    'objectives_with_questions': ch.objectives_with_questions,
                    'objectives_ai_only': ch.objectives_ai_only,
                    'coverage_pct': ch.coverage_pct,
                    'coverage_source': ch.coverage_source,
                    'relevance_score': ch.relevance_score,
                    'exam_appearance_rate': ch.exam_appearance_rate,
                    'relevance_trend': ch.relevance_trend,
                    'prognosis_probability': ch.prognosis_probability,
                    'prognosis_confidence': ch.prognosis_confidence,
                    'user_proficiency': ch.user_proficiency,
                    'user_severity': ch.user_severity,
                    'intelligence_score': ch.intelligence_score,
                }
                for ch in self.chapters
            ],
        }
