"""
Exam Course Plan — Domain Value Objects.

Describes the structure of an auto-generated IHK exam course
before it's persisted to the database.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class LMMapping:
    """Maps a question_type to a target learning method."""
    question_type: str
    target_lm_type: int
    transform_fn: str


@dataclass(frozen=True)
class ChapterPlan:
    """Plan for a single chapter (= one topic)."""
    topic: str
    question_ids: List[str]
    lm_types: List[int]
    point_weight: float
    question_count: int


@dataclass(frozen=True)
class ExamCoursePlan:
    """Complete plan for an auto-generated exam course."""
    title: str
    exam_type: str
    region: str
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
            'total_questions': self.total_questions,
            'total_points': self.total_points,
            'chapters': [
                {
                    'topic': ch.topic,
                    'question_count': ch.question_count,
                    'lm_types': ch.lm_types,
                    'point_weight': ch.point_weight,
                }
                for ch in self.chapters
            ],
            'simulation_exam_ids': self.simulation_exam_ids,
        }
