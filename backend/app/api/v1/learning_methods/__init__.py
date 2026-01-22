"""Learning Methods Module - Public and Admin APIs"""

from app.api.v1.learning_methods.core import learning_methods_bp
from app.api.v1.learning_methods.chapters import chapter_theory_bp
from app.api.v1.learning_methods.explanations import lesson_explanations_bp
from app.api.v1.learning_methods.videos import lesson_videos_bp
from app.api.v1.learning_methods.catalog import catalog_bp as learning_methods_catalog_bp

__all__ = [
    'learning_methods_bp',
    'chapter_theory_bp',
    'lesson_explanations_bp',
    'lesson_videos_bp',
    'learning_methods_catalog_bp'
]
