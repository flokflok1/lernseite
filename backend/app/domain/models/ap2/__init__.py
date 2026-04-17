"""
AP2 Trainer Domain Models — FISI FA 235 Baden-Württemberg.

Active Recall (Blurt/Cued/Application) + SM-2 Spaced Repetition
+ beschriftbare Anlagen + IHK-Stil Prüfungssimulation.

DDD Layer: Domain — NO Flask, DB, or Infrastructure imports.
"""

from .enums import (
    Bereich,
    Priority,
    ItemType,
    Phase,
    AnlageType,
    SessionType,
    HotspotType,
)
from .topic import Topic
from .anlage import Anlage, Hotspot
from .learning_item import LearningItem, GradingCriterion
from .attempt import Attempt, AttemptFeedback
from .review_schedule import ReviewScheduleEntry, SM2Result
from .topic_mastery import TopicMastery
from .cheatsheet import Cheatsheet
from .study_session import StudySession

__all__ = [
    # Enums
    'Bereich', 'Priority', 'ItemType', 'Phase',
    'AnlageType', 'SessionType', 'HotspotType',
    # Entities / VOs
    'Topic', 'Anlage', 'Hotspot',
    'LearningItem', 'GradingCriterion',
    'Attempt', 'AttemptFeedback',
    'ReviewScheduleEntry', 'SM2Result',
    'TopicMastery', 'Cheatsheet', 'StudySession',
]
