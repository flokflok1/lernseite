"""
Exam Systems Domain

Domain for managing exam systems (IHK, Practical, Chapter Completion).

Journeys:
- Admin Journey: Exam template management (7 endpoints)
- User Journey: Exam execution and results (9 endpoints)

Exam Types:
1. IHK Exam System - IHK/Kammer standard exams with certification
2. Practical Exam Engine - Multi-step practical exams with grading
3. Chapter Completion System - Comprehensive chapter exams with unlock

Total: 16 Endpoints

Phase: 5.3.2 - Exam Systems Domain Implementation
"""

from .journeys import ALL_JOURNEY_BLUEPRINTS

__all__ = ['ALL_JOURNEY_BLUEPRINTS']
