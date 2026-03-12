"""
Exam & Assessment - System Features

4 Features total:
- simulations/            # Exam Simulations - IHK-style exam simulations (IMPLEMENTED)
- ihk_exam.py             # IHK Exam System - IHK-style exam format (STUB)
- practical_exam.py       # Practical Exam Engine - Hands-on assessments (STUB)
- chapter_completion.py   # Chapter Completion System - Progress tracking (STUB)

Status: 1 implemented, 3 stubs
"""

# Import implemented features
from app.api.v1.public.system_features.exam.simulations import exams_bp
from app.api.v1.public.system_features.exam.question_generator import question_generator_bp

# TODO: Uncomment when stub features are implemented
# from app.api.v1.public.system_features.exam.ihk_exam import ihk_exam_bp
# from app.api.v1.public.system_features.exam.practical_exam import practical_exam_bp
# from app.api.v1.public.system_features.exam.chapter_completion import chapter_completion_bp

__all__ = ['exams_bp', 'question_generator_bp']
