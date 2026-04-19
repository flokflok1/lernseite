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
from .module import (
    Module,
    ModuleProgress,
    ModuleStatus,
    AttemptPhase,
    AttemptSource,
    ModuleAttemptLog,
    MASTERY_PASS_THRESHOLD,
    MASTERY_STREAK_REQUIRED,
    SAME_DAY_RECALL_DELAY_HOURS,
    SPOTCHECK_SCHEDULE_DAYS,
)
from .skill import (
    UserLearningPrefs,
    ItemSkill,
    RecoveryMode,
    StuetzradDefault,
    MasteryStrictness,
    ABS_MIN_TARGET,
    ABS_MAX_TARGET,
    DEFAULT_BASE_TARGET,
    DEFAULT_MAX_TARGET,
    SOFT_FAIL_THRESHOLD,
    AUTO_STUETZRAD_THRESHOLD,
    PAUSE_HINT_THRESHOLD,
)

__all__ = [
    # Enums
    'Bereich', 'Priority', 'ItemType', 'Phase',
    'AnlageType', 'SessionType', 'HotspotType',
    'ModuleStatus', 'AttemptPhase', 'AttemptSource',
    # Entities / VOs
    'Topic', 'Anlage', 'Hotspot',
    'LearningItem', 'GradingCriterion',
    'Attempt', 'AttemptFeedback',
    'ReviewScheduleEntry', 'SM2Result',
    'TopicMastery', 'Cheatsheet', 'StudySession',
    'Module', 'ModuleProgress', 'ModuleAttemptLog',
    'UserLearningPrefs', 'ItemSkill',
    'RecoveryMode', 'StuetzradDefault', 'MasteryStrictness',
    # Constants
    'MASTERY_PASS_THRESHOLD', 'MASTERY_STREAK_REQUIRED',
    'SAME_DAY_RECALL_DELAY_HOURS', 'SPOTCHECK_SCHEDULE_DAYS',
    'ABS_MIN_TARGET', 'ABS_MAX_TARGET',
    'DEFAULT_BASE_TARGET', 'DEFAULT_MAX_TARGET',
    'SOFT_FAIL_THRESHOLD', 'AUTO_STUETZRAD_THRESHOLD', 'PAUSE_HINT_THRESHOLD',
]
