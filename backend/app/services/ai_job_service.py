"""
LernsystemX AI Job Service

Business logic layer for AI Job management:
- Job creation and initialization
- Status and progress updates
- Output data management
- Error handling and retry logic

Phase B24-05 - ISO 27001:2013 compliant
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

from app.repositories.ai_job_repository import AIJobRepository

# Setup logger
logger = logging.getLogger(__name__)


class AIJobService:
    """
    Service for AI Job operations

    Provides business logic for:
    - Creating and initializing AI jobs
    - Updating job status and progress
    - Managing output data
    - Error handling
    """

    # Job type constants
    TYPE_COURSE_FROM_PDF = 'course_from_pdf'
    TYPE_MODULE_AUTOGEN = 'module_autogen'
    TYPE_LESSON_AUTOGEN = 'lesson_autogen'

    # Job status constants (DB uses 'queued' instead of 'pending')
    STATUS_PENDING = 'queued'  # Alias for backwards compatibility
    STATUS_QUEUED = 'queued'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_CANCELLED = 'cancelled'

    VALID_TYPES = [TYPE_COURSE_FROM_PDF, TYPE_MODULE_AUTOGEN, TYPE_LESSON_AUTOGEN]
    VALID_STATUSES = [STATUS_QUEUED, STATUS_PROCESSING, STATUS_COMPLETED, STATUS_FAILED, STATUS_CANCELLED]

    @staticmethod
    def create_job(
        user_id: str,
        job_type: str,
        input_file: Optional[str] = None,
        input_prompt: Optional[str] = None,
        course_id: Optional[str] = None,
        prompt_id: Optional[str] = None,
        storage_path: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new AI job

        Args:
            user_id: User UUID
            job_type: Job type (course_from_pdf, module_autogen, lesson_autogen)
            input_file: Optional input file path/name
            input_prompt: Optional user prompt
            course_id: Optional course ID (for module/lesson generation)
            prompt_id: Optional prompt template ID
            storage_path: Optional full storage path for uploaded file
            model: Optional AI model override (Phase C3.4)

        Returns:
            Created job dict

        Raises:
            ValueError: If job_type is invalid

        Example:
            >>> job = AIJobService.create_job(
            ...     user_id='uuid',
            ...     job_type='course_from_pdf',
            ...     input_file='python_basics.pdf',
            ...     input_prompt='Create a beginner Python course',
            ...     model='gpt-4o'
            ... )
        """
        # Validate job type
        if job_type not in AIJobService.VALID_TYPES:
            raise ValueError(f'Invalid job type: {job_type}. Must be one of: {", ".join(AIJobService.VALID_TYPES)}')

        # Create job
        job_data = {
            'user_id': user_id,
            'type': job_type,
            'status': AIJobService.STATUS_PENDING,
            'progress': 0,
            'input_file': input_file,
            'input_prompt': input_prompt,
            'course_id': course_id,
            'prompt_id': prompt_id,
            'storage_path': storage_path,
            'model': model
        }

        job = AIJobRepository.create(job_data)

        logger.info(f'AI job created: {job["id"]} (type={job_type}, user={user_id})')

        return job

    @staticmethod
    def get_job(job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job by ID

        Args:
            job_id: Job UUID

        Returns:
            Job dict or None
        """
        return AIJobRepository.find_by_id(job_id)

    @staticmethod
    def get_user_jobs(user_id: str, limit: int = 50) -> list[Dict[str, Any]]:
        """
        Get all jobs for a user

        Args:
            user_id: User UUID
            limit: Maximum number of jobs

        Returns:
            List of jobs
        """
        return AIJobRepository.find_by_user(user_id, limit)

    @staticmethod
    def update_status(job_id: str, status: str) -> Optional[Dict[str, Any]]:
        """
        Update job status

        Args:
            job_id: Job UUID
            status: New status

        Returns:
            Updated job or None

        Raises:
            ValueError: If status is invalid
        """
        if status not in AIJobService.VALID_STATUSES:
            raise ValueError(f'Invalid status: {status}. Must be one of: {", ".join(AIJobService.VALID_STATUSES)}')

        job = AIJobRepository.update_status(job_id, status)

        if job:
            logger.info(f'AI job status updated: {job_id} → {status}')

        return job

    @staticmethod
    def update_progress(job_id: str, progress: int) -> Optional[Dict[str, Any]]:
        """
        Update job progress

        Args:
            job_id: Job UUID
            progress: Progress percentage (0-100)

        Returns:
            Updated job or None

        Raises:
            ValueError: If progress is out of range
        """
        if not (0 <= progress <= 100):
            raise ValueError(f'Progress must be between 0 and 100, got: {progress}')

        job = AIJobRepository.update_progress(job_id, progress)

        if job:
            logger.debug(f'AI job progress updated: {job_id} → {progress}%')

        return job

    @staticmethod
    def update_output(job_id: str, output_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update job output data

        Args:
            job_id: Job UUID
            output_data: Output data dict

        Returns:
            Updated job or None
        """
        job = AIJobRepository.update_output(job_id, output_data)

        if job:
            logger.info(f'AI job output updated: {job_id}')

        return job

    @staticmethod
    def attach_course(job_id: str, course_id: str) -> Optional[Dict[str, Any]]:
        """
        Attach course to job

        Args:
            job_id: Job UUID
            course_id: Course UUID

        Returns:
            Updated job or None
        """
        job = AIJobRepository.attach_course(job_id, course_id)

        if job:
            logger.info(f'Course attached to AI job: {job_id} → course {course_id}')

        return job

    @staticmethod
    def fail_job(job_id: str, error_message: str) -> Optional[Dict[str, Any]]:
        """
        Mark job as failed with error message

        Args:
            job_id: Job UUID
            error_message: Error description

        Returns:
            Updated job or None
        """
        job = AIJobRepository.fail_job(job_id, error_message)

        if job:
            logger.error(f'AI job failed: {job_id} - {error_message}')

        return job

    @staticmethod
    def cancel_job(job_id: str) -> Optional[Dict[str, Any]]:
        """
        Cancel a job (only if pending or processing)

        Args:
            job_id: Job UUID

        Returns:
            Updated job or None
        """
        job = AIJobRepository.cancel_job(job_id)

        if job:
            logger.info(f'AI job cancelled: {job_id}')
        else:
            logger.warning(f'AI job could not be cancelled (already completed/failed?): {job_id}')

        return job

    @staticmethod
    def complete_job(job_id: str, output_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Mark job as completed

        Args:
            job_id: Job UUID
            output_data: Optional final output data

        Returns:
            Updated job or None
        """
        job = AIJobRepository.complete_job(job_id, output_data)

        if job:
            logger.info(f'AI job completed: {job_id}')

        return job

    @staticmethod
    def get_job_stats(user_id: str) -> Dict[str, Any]:
        """
        Get job statistics for a user

        Args:
            user_id: User UUID

        Returns:
            Stats dict with counts per status
        """
        return AIJobRepository.get_stats_by_user(user_id)

    @staticmethod
    def start_processing(job_id: str) -> Optional[Dict[str, Any]]:
        """
        Mark job as processing

        Args:
            job_id: Job UUID

        Returns:
            Updated job or None
        """
        return AIJobService.update_status(job_id, AIJobService.STATUS_PROCESSING)

    @staticmethod
    def validate_job_transition(current_status: str, new_status: str) -> bool:
        """
        Validate if status transition is allowed

        Args:
            current_status: Current job status
            new_status: Desired new status

        Returns:
            True if transition is valid, False otherwise
        """
        # Define allowed transitions (use 'queued' as primary status)
        allowed_transitions = {
            'queued': ['processing', 'cancelled'],
            'pending': ['processing', 'cancelled'],  # Legacy alias
            'processing': ['completed', 'failed', 'cancelled'],
            'completed': [],  # Terminal state
            'failed': [],  # Terminal state
            'cancelled': []  # Terminal state
        }

        if current_status not in allowed_transitions:
            return False

        return new_status in allowed_transitions[current_status]
