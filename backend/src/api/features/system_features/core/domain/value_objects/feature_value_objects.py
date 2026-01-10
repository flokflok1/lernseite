"""
System Features Domain - Value Objects

Immutable value objects representing System Features domain concepts.

Value Objects:
- FeatureScope: Defines where a feature is applied (course/chapter/lesson)
- FeatureConfig: Configuration for a specific feature
- FeatureCategory: Category grouping for features
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class FeatureScopeType(str, Enum):
    """Feature scope types"""
    COURSE = "course"
    CHAPTER = "chapter"
    LESSON = "lesson"


class FeatureCategoryType(str, Enum):
    """System Feature categories"""
    INTERACTIVE_TOOLS = "interactive_tools"
    META_FEATURES = "meta_features"
    VISUALIZATION = "visualization"
    TUTOR = "tutor"
    GAMIFICATION = "gamification"
    LEARNING_PATHS = "learning_paths"
    COLLABORATION = "collaboration"
    EXAM_SYSTEMS = "exam_systems"
    IT_ENVIRONMENTS = "it_environments"
    AUDIO = "audio"


@dataclass(frozen=True)
class FeatureScope:
    """
    Feature Scope Value Object.

    Defines where a feature is applied (course/chapter/lesson).
    Immutable.

    Attributes:
        scope_type: Type of scope (course, chapter, lesson)
        scope_id: ID of the scope target (course_id, chapter_id, lesson_id)
    """
    scope_type: FeatureScopeType
    scope_id: str

    def __post_init__(self):
        """Validate scope"""
        if not self.scope_id:
            raise ValueError("scope_id cannot be empty")

    def is_course_level(self) -> bool:
        """Check if this is a course-level scope"""
        return self.scope_type == FeatureScopeType.COURSE

    def is_chapter_level(self) -> bool:
        """Check if this is a chapter-level scope"""
        return self.scope_type == FeatureScopeType.CHAPTER

    def is_lesson_level(self) -> bool:
        """Check if this is a lesson-level scope"""
        return self.scope_type == FeatureScopeType.LESSON


@dataclass(frozen=True)
class FeatureConfig:
    """
    Feature Configuration Value Object.

    Represents configuration for a specific feature.
    Immutable.

    Attributes:
        feature_code: Unique feature code (e.g., 'socratic_dialog')
        is_enabled: Whether the feature is enabled
        config: Optional feature-specific configuration
    """
    feature_code: str
    is_enabled: bool
    config: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate configuration"""
        if not self.feature_code:
            raise ValueError("feature_code cannot be empty")

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value safely.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        if not self.config:
            return default
        return self.config.get(key, default)

    def has_config(self) -> bool:
        """Check if this feature has custom configuration"""
        return self.config is not None and len(self.config) > 0


@dataclass(frozen=True)
class FeatureCategory:
    """
    Feature Category Value Object.

    Represents a category grouping for system features.
    Immutable.

    Attributes:
        category_type: Type of category
        display_name: Human-readable name
        description: Category description
    """
    category_type: FeatureCategoryType
    display_name: str
    description: Optional[str] = None

    @staticmethod
    def from_string(category_str: str) -> 'FeatureCategory':
        """
        Create FeatureCategory from string.

        Args:
            category_str: Category string (e.g., 'tutor')

        Returns:
            FeatureCategory instance

        Raises:
            ValueError: If category string is invalid
        """
        category_map = {
            "interactive_tools": ("Interactive Tools", "Interaktive Werkzeuge wie Whiteboard, Speech-to-Text"),
            "meta_features": ("Meta Features", "Übergreifende Features wie Timer"),
            "visualization": ("Visualization", "Visualisierungs-Tools wie Mindmap-Generator"),
            "tutor": ("Tutor & Coaching", "KI-Tutoren und Coaching-Features"),
            "gamification": ("Gamification", "Gamification-Features wie XP, Quests, Adaptive Difficulty"),
            "learning_paths": ("Learning Paths", "Lernpfad-Generierung und -Optimierung"),
            "collaboration": ("Collaboration", "Kollaborations-Features wie Peer Review, Team-Case"),
            "exam_systems": ("Exam Systems", "Prüfungssysteme wie IHK-Prüfungen"),
            "it_environments": ("IT Environments", "IT-Umgebungen wie Code-Sandbox, Terminal"),
            "audio": ("Audio", "Audio-Features wie Speech-to-Text")
        }

        if category_str not in category_map:
            raise ValueError(f"Invalid category: {category_str}")

        display_name, description = category_map[category_str]
        return FeatureCategory(
            category_type=FeatureCategoryType(category_str),
            display_name=display_name,
            description=description
        )
