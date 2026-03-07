"""
Exam Intelligence Domain Value Objects

Immutable value objects for the Exam Intelligence Layer:
- TopicWeakness: A single topic's weakness score for a user
- WeaknessProfile: Aggregated weakness analysis per exam type
- ExamContext: Exam-relevant context injected into AI prompts
"""

from dataclasses import dataclass

VALID_TRENDS = frozenset({'improving', 'stable', 'declining'})
VALID_GOAL_STATUSES = frozenset({'active', 'passed', 'paused', 'planned'})


@dataclass(frozen=True)
class TopicWeakness:
    """A user's weakness on a single exam topic."""

    topic_key: str
    score: float
    attempts: int = 0
    trend: str = 'stable'

    @classmethod
    def from_dict(cls, data: dict) -> 'TopicWeakness':
        topic_key = (data.get('topic_key') or '').strip()
        if not topic_key:
            raise ValueError('TopicWeakness: topic_key must not be empty')
        trend = data.get('trend', 'stable')
        if trend not in VALID_TRENDS:
            trend = 'stable'
        return cls(
            topic_key=topic_key,
            score=float(data.get('score', 0.0)),
            attempts=int(data.get('attempts', 0)),
            trend=trend,
        )

    def to_dict(self) -> dict:
        return {
            'topic_key': self.topic_key,
            'score': self.score,
            'attempts': self.attempts,
            'trend': self.trend,
        }


@dataclass(frozen=True)
class WeaknessProfile:
    """Aggregated weakness profile for a user + exam type."""

    exam_type: str
    weaknesses: tuple
    overall_score: float
    recommendation: str = ''

    @classmethod
    def from_dict(cls, data: dict) -> 'WeaknessProfile':
        exam_type = (data.get('exam_type') or '').strip()
        if not exam_type:
            raise ValueError('WeaknessProfile: exam_type must not be empty')
        raw_weaknesses = data.get('weaknesses') or []
        weaknesses = tuple(
            TopicWeakness.from_dict(w) if isinstance(w, dict) else w
            for w in raw_weaknesses
        )
        return cls(
            exam_type=exam_type,
            weaknesses=weaknesses,
            overall_score=float(data.get('overall_score', 0.0)),
            recommendation=data.get('recommendation', ''),
        )

    def to_dict(self) -> dict:
        return {
            'exam_type': self.exam_type,
            'weaknesses': [w.to_dict() for w in self.weaknesses],
            'overall_score': self.overall_score,
            'recommendation': self.recommendation,
        }


@dataclass(frozen=True)
class ExamContext:
    """Exam-relevant context for AI prompt enrichment."""

    exam_type: str
    relevant_topics: tuple
    hard_topics: tuple
    passing_score: int = 50

    @classmethod
    def from_dict(cls, data: dict) -> 'ExamContext':
        exam_type = (data.get('exam_type') or '').strip()
        if not exam_type:
            raise ValueError('ExamContext: exam_type must not be empty')
        return cls(
            exam_type=exam_type,
            relevant_topics=tuple(data.get('relevant_topics') or []),
            hard_topics=tuple(data.get('hard_topics') or []),
            passing_score=int(data.get('passing_score', 50)),
        )

    def to_dict(self) -> dict:
        return {
            'exam_type': self.exam_type,
            'relevant_topics': list(self.relevant_topics),
            'hard_topics': list(self.hard_topics),
            'passing_score': self.passing_score,
        }

    def to_prompt_context(self) -> dict:
        """Return a flat dict suitable for prompt template variables."""
        return {
            'exam_type': self.exam_type,
            'relevant_topics_csv': ', '.join(self.relevant_topics),
            'hard_topics_csv': ', '.join(self.hard_topics),
            'passing_score': self.passing_score,
            'has_exam_context': True,
        }
