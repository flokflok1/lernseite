"""ProgramAdminService — admin CRUD for programs and program types.

DDD: Application layer — orchestrates Infrastructure calls.
"""
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ProgramAdminService:
    """Admin operations for programs and program types."""

    # --- Programs ---
    @staticmethod
    def list_programs() -> List[Dict[str, Any]]:
        from app.infrastructure.persistence.repositories.exams.programs import (
            ExamProgramRepository,
        )
        return ExamProgramRepository.find_with_parts()

    @staticmethod
    def create_program(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        from app.infrastructure.persistence.repositories.exams.programs import (
            ExamProgramRepository,
        )
        return ExamProgramRepository.create(data)

    @staticmethod
    def update_program(program_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        from app.infrastructure.persistence.repositories.exams.programs import (
            ExamProgramRepository,
        )
        return ExamProgramRepository.update(program_id, data)

    @staticmethod
    def trash_program(program_id: int) -> bool:
        from app.infrastructure.persistence.repositories.exams.programs import (
            ExamProgramRepository,
        )
        return ExamProgramRepository.trash_by_id(program_id)

    # --- Program Types ---
    @staticmethod
    def list_types() -> List[Dict[str, Any]]:
        from app.infrastructure.persistence.repositories.exams.program_types import (
            ProgramTypeRepository,
        )
        return ProgramTypeRepository.find_all()

    @staticmethod
    def create_type(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        from app.infrastructure.persistence.repositories.exams.program_types import (
            ProgramTypeRepository,
        )
        return ProgramTypeRepository.create(data)

    @staticmethod
    def update_type(type_key: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        from app.infrastructure.persistence.repositories.exams.program_types import (
            ProgramTypeRepository,
        )
        return ProgramTypeRepository.update(type_key, data)

    @staticmethod
    def delete_type(type_key: str) -> bool:
        from app.infrastructure.persistence.repositories.exams.program_types import (
            ProgramTypeRepository,
        )
        return ProgramTypeRepository.delete(type_key)

    # --- Exam Types ---

    @staticmethod
    def list_exam_types(program_id: int) -> List[Dict[str, Any]]:
        from app.infrastructure.persistence.repositories.exams.exam_type_registry import (
            ExamTypeRegistryRepository,
        )
        return ExamTypeRegistryRepository.find_by_program(program_id)

    @staticmethod
    def create_exam_type(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        from app.infrastructure.persistence.repositories.exams.exam_type_registry import (
            ExamTypeRegistryRepository,
        )
        return ExamTypeRegistryRepository.create(data)

    @staticmethod
    def update_exam_type(exam_type: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        from app.infrastructure.persistence.repositories.exams.exam_type_registry import (
            ExamTypeRegistryRepository,
        )
        return ExamTypeRegistryRepository.update(exam_type, data)

    @staticmethod
    def delete_exam_type(exam_type: str) -> bool:
        from app.infrastructure.persistence.repositories.exams.exam_type_registry import (
            ExamTypeRegistryRepository,
        )
        if ExamTypeRegistryRepository.has_dependent_exams(exam_type):
            raise ValueError(
                f'Exam type {exam_type!r} has dependent exams — cannot delete'
            )
        return ExamTypeRegistryRepository.delete(exam_type)
