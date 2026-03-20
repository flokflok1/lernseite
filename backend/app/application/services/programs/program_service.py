"""ProgramService — user-facing program operations.

Orchestrates enrollment, program listing, and detail retrieval.
DDD: Application layer — imports Infrastructure repositories.
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class ProgramService:
    """User-facing program operations."""

    @staticmethod
    def list_user_programs(user_id: str) -> List[Dict[str, Any]]:
        """Get programs the user is enrolled in, with stats."""
        from app.infrastructure.persistence.repositories.exams.programs import (
            ExamProgramRepository,
        )
        return ExamProgramRepository.find_enrolled_programs(user_id)

    @staticmethod
    def list_available_programs() -> List[Dict[str, Any]]:
        """Get all active programs (catalog)."""
        from app.infrastructure.persistence.repositories.exams.programs import (
            ExamProgramRepository,
        )
        return ExamProgramRepository.find_available_programs()

    @staticmethod
    def enroll(user_id: str, program_id: int) -> bool:
        """Enroll user in a program."""
        from app.infrastructure.persistence.repositories.exams.programs import (
            ExamProgramRepository,
        )
        return ExamProgramRepository.enroll_user(user_id, program_id)

    @staticmethod
    def unenroll(user_id: str, program_id: int) -> bool:
        """Remove user enrollment."""
        from app.infrastructure.persistence.repositories.exams.programs import (
            ExamProgramRepository,
        )
        return ExamProgramRepository.unenroll_user(user_id, program_id)

    @staticmethod
    def get_program_detail(program_id: int, user_id: str) -> Dict[str, Any]:
        """Get program with trainer stats."""
        from app.infrastructure.persistence.repositories.exams.programs import (
            ExamProgramRepository,
        )
        from app.infrastructure.persistence.repositories.exams.trainer import (
            ExamTrainerRepository,
        )
        programs = ExamProgramRepository.find_enrolled_programs(user_id)
        prog = next((p for p in programs if p['program_id'] == program_id), None)
        if not prog:
            return {}

        topics = ExamTrainerRepository.find_topics_with_stats(user_id)

        return {
            'program': prog,
            'topics': topics,
        }
