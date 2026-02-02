"""
LernsystemX AI Job Repository

Data access layer for AI Jobs:
- CRUD operations for AI content generation jobs
- Job status management
- Progress tracking
- Output data storage

Phase B24-05 - ISO 27001:2013 compliant
"""

from typing import Optional, Dict, List, Any
from datetime import datetime
import json

from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query, insert_returning


class AIJobRepository:
    """
    Repository for AI Job entity

    Handles all database operations for AI jobs including:
    - Job creation and management
    - Status and progress updates
    - Output data storage (JSONB)
    - Error handling

    Database columns:
    - job_id (PK)
    - user_id, organisation_id
    - job_type, input_data (JSONB), output_data (JSONB)
    - status (queued, processing, completed, failed, cancelled)
    - progress_percentage, priority
    - error_message, retry_count, max_retries
    - scheduled_for, started_at, completed_at, created_at
    - storage_path, prompt_id
    """

    table_name = 'ai_pipeline.ai_jobs'

    @classmethod
    def create(cls, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new AI job

        Args:
            job_data: Job data including:
                - user_id: UUID (required)
                - job_type: str (required) - course_from_pdf | module_autogen | lesson_autogen
                - input_data: dict (optional) - JSONB input data
                - prompt_id: UUID (optional) - reference to course_prompts
                - storage_path: str (optional) - full file path
                - organisation_id: UUID (optional)
                - priority: int (optional, default 0)

        Returns:
            Created job with job_id

        Example:
            >>> job = AIJobRepository.create({
            ...     'user_id': 'uuid',
            ...     'job_type': 'course_from_pdf',
            ...     'input_data': {'file': 'example.pdf', 'prompt': 'Create a Python course'}
            ... })
        """
        # Build input_data JSONB from legacy fields if present
        input_data = job_data.get('input_data', {})
        if 'input_file' in job_data and job_data['input_file']:
            input_data['file'] = job_data.pop('input_file')
        if 'input_prompt' in job_data and job_data['input_prompt']:
            input_data['prompt'] = job_data.pop('input_prompt')
        # Always remove course_id from job_data (not a DB column), store in input_data if not None
        if 'course_id' in job_data:
            course_id_val = job_data.pop('course_id')
            if course_id_val:
                input_data['course_id'] = course_id_val

        # Map legacy 'type' to 'job_type'
        if 'type' in job_data:
            job_data['job_type'] = job_data.pop('type')

        # Map legacy 'progress' to 'progress_percentage'
        if 'progress' in job_data:
            job_data['progress_percentage'] = job_data.pop('progress')

        # Map legacy 'pending' status to 'queued'
        if job_data.get('status') == 'pending':
            job_data['status'] = 'queued'

        defaults = {
            'status': 'queued',
            'progress_percentage': 0,
            'priority': 0,
            'output_data': None,
            'prompt_id': None,
            'storage_path': None,
            'organisation_id': None,
            'model': None  # Phase C3.4: AI Model Override
        }

        params = {**defaults, **job_data}
        params['input_data'] = json.dumps(input_data) if input_data else '{}'

        result = insert_returning(cls.table_name, params, returning='*')
        if result:
            # Add 'id' alias for backwards compatibility
            result['id'] = result['job_id']
        return result

    @classmethod
    def find_by_id(cls, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Find job by ID

        Args:
            job_id: Job UUID

        Returns:
            Job dict or None
        """
        query = """
            SELECT
                j.*,
                u.email AS user_email
            FROM ai_pipeline.ai_jobs j
            LEFT JOIN core.users u ON j.user_id = u.user_id
            WHERE j.job_id = %s
        """

        result = fetch_one(query, (job_id,))
        if result:
            # Add 'id' alias for backwards compatibility
            result['id'] = result['job_id']
        return result

    @classmethod
    def find_by_user(cls, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Find all jobs for a user

        Args:
            user_id: User UUID
            limit: Maximum number of jobs to return

        Returns:
            List of jobs
        """
        query = """
            SELECT j.*
            FROM ai_pipeline.ai_jobs j
            WHERE j.user_id = %s
            ORDER BY j.created_at DESC
            LIMIT %s
        """

        results = fetch_all(query, (user_id, limit))
        # Add 'id' alias for backwards compatibility
        for result in results:
            result['id'] = result['job_id']
        return results

    @classmethod
    def find_by_status(cls, status: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Find jobs by status

        Args:
            status: Job status (pending, processing, completed, failed, cancelled)
            limit: Maximum number of jobs to return

        Returns:
            List of jobs
        """
        query = """
            SELECT j.*
            FROM ai_pipeline.ai_jobs j
            WHERE j.status = %s
            ORDER BY j.created_at ASC
            LIMIT %s
        """

        return fetch_all(query, (status, limit))

    @classmethod
    def update_status(cls, job_id: str, status: str) -> Optional[Dict[str, Any]]:
        """
        Update job status

        Args:
            job_id: Job UUID
            status: New status (queued, processing, completed, failed, cancelled)

        Returns:
            Updated job or None
        """
        # Map legacy 'pending' to 'queued'
        if status == 'pending':
            status = 'queued'

        query = """
            UPDATE ai_pipeline.ai_jobs
            SET status = %s
            WHERE job_id = %s
            RETURNING *
        """

        result = fetch_one(query, (status, job_id))
        if result:
            result['id'] = result['job_id']
        return result

    @classmethod
    def update_progress(cls, job_id: str, progress: int) -> Optional[Dict[str, Any]]:
        """
        Update job progress

        Args:
            job_id: Job UUID
            progress: Progress percentage (0-100)

        Returns:
            Updated job or None
        """
        query = """
            UPDATE ai_pipeline.ai_jobs
            SET progress_percentage = %s
            WHERE job_id = %s
            RETURNING *
        """

        result = fetch_one(query, (progress, job_id))
        if result:
            result['id'] = result['job_id']
        return result

    @classmethod
    def update_output(cls, job_id: str, output_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update job output data

        Args:
            job_id: Job UUID
            output_data: Output data (will be stored as JSONB)

        Returns:
            Updated job or None
        """
        query = """
            UPDATE ai_pipeline.ai_jobs
            SET output_data = %s::jsonb
            WHERE job_id = %s
            RETURNING *
        """

        output_json = json.dumps(output_data) if output_data else None

        result = fetch_one(query, (output_json, job_id))
        if result:
            result['id'] = result['job_id']
        return result

    @classmethod
    def attach_course(cls, job_id: str, course_id: str) -> Optional[Dict[str, Any]]:
        """
        Attach course to job by storing in input_data

        Args:
            job_id: Job UUID
            course_id: Course UUID

        Returns:
            Updated job or None
        """
        # Store course_id in input_data JSONB
        query = """
            UPDATE ai_pipeline.ai_jobs
            SET input_data = input_data || %s::jsonb
            WHERE job_id = %s
            RETURNING *
        """

        result = fetch_one(query, (json.dumps({'course_id': course_id}), job_id))
        if result:
            result['id'] = result['job_id']
        return result

    @classmethod
    def fail_job(cls, job_id: str, error_message: str) -> Optional[Dict[str, Any]]:
        """
        Mark job as failed with error message

        Args:
            job_id: Job UUID
            error_message: Error description

        Returns:
            Updated job or None
        """
        query = """
            UPDATE ai_pipeline.ai_jobs
            SET status = 'failed', error_message = %s
            WHERE job_id = %s
            RETURNING *
        """

        result = fetch_one(query, (error_message, job_id))
        if result:
            result['id'] = result['job_id']
        return result

    @classmethod
    def cancel_job(cls, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Cancel a job

        Args:
            job_id: Job UUID

        Returns:
            Updated job or None
        """
        query = """
            UPDATE ai_pipeline.ai_jobs
            SET status = 'cancelled'
            WHERE job_id = %s
            AND status IN ('queued', 'processing')
            RETURNING *
        """

        result = fetch_one(query, (job_id,))
        if result:
            result['id'] = result['job_id']
        return result

    @classmethod
    def complete_job(cls, job_id: str, output_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Mark job as completed

        Args:
            job_id: Job UUID
            output_data: Optional final output data

        Returns:
            Updated job or None
        """
        if output_data:
            query = """
                UPDATE ai_pipeline.ai_jobs
                SET status = 'completed', progress_percentage = 100, output_data = %s::jsonb, completed_at = NOW()
                WHERE job_id = %s
                RETURNING *
            """
            output_json = json.dumps(output_data)
            result = fetch_one(query, (output_json, job_id))
        else:
            query = """
                UPDATE ai_pipeline.ai_jobs
                SET status = 'completed', progress_percentage = 100, completed_at = NOW()
                WHERE job_id = %s
                RETURNING *
            """
            result = fetch_one(query, (job_id,))

        if result:
            result['id'] = result['job_id']
        return result

    @classmethod
    def delete(cls, job_id: str) -> bool:
        """
        Delete a job

        Args:
            job_id: Job UUID

        Returns:
            True if deleted, False otherwise
        """
        query = "DELETE FROM ai_pipeline.ai_jobs WHERE job_id = %s"
        return execute_query(query, (job_id,))

    @classmethod
    def get_stats_by_user(cls, user_id: str) -> Dict[str, Any]:
        """
        Get job statistics for a user

        Args:
            user_id: User UUID

        Returns:
            Stats dict with counts per status
        """
        query = """
            SELECT
                COUNT(*) FILTER (WHERE status = 'queued') AS pending_count,
                COUNT(*) FILTER (WHERE status = 'processing') AS processing_count,
                COUNT(*) FILTER (WHERE status = 'completed') AS completed_count,
                COUNT(*) FILTER (WHERE status = 'failed') AS failed_count,
                COUNT(*) FILTER (WHERE status = 'cancelled') AS cancelled_count,
                COUNT(*) AS total_count
            FROM ai_pipeline.ai_jobs
            WHERE user_id = %s
        """

        return fetch_one(query, (user_id,)) or {
            'pending_count': 0,
            'processing_count': 0,
            'completed_count': 0,
            'failed_count': 0,
            'cancelled_count': 0,
            'total_count': 0
        }

    @classmethod
    def get_recent_jobs(cls, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent jobs (all users, for admin)

        Args:
            limit: Number of jobs to return

        Returns:
            List of recent jobs
        """
        query = """
            SELECT
                j.*,
                u.email AS user_email
            FROM ai_pipeline.ai_jobs j
            LEFT JOIN core.users u ON j.user_id = u.user_id
            ORDER BY j.created_at DESC
            LIMIT %s
        """

        results = fetch_all(query, (limit,))
        # Add 'id' alias for backwards compatibility
        for result in results:
            result['id'] = result['job_id']
        return results


# Alias for backward compatibility
AIJobsRepository = AIJobRepository
