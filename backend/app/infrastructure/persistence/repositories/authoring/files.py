"""
Repository for authoring_files table (Multi-File Upload System)
"""
from typing import Dict, List, Optional
import logging

from app.infrastructure.persistence.repositories.core.base import BaseRepository

logger = logging.getLogger(__name__)


class AuthoringFilesRepository(BaseRepository):
    """Repository for managing uploaded files in authoring sessions"""

    @staticmethod
    def create_file(
        session_id: str,
        filename: str,
        file_type: str,
        file_size_bytes: int,
        storage_path: str,
        uploaded_by: str
    ) -> Optional[str]:
        """
        Create a new file record.

        Args:
            session_id: UUID of authoring session
            filename: Original filename
            file_type: File type (pdf, docx, etc.)
            file_size_bytes: File size in bytes
            storage_path: Path where file is stored
            uploaded_by: User who uploaded the file

        Returns:
            file_id if successful
        """
        query = """
            INSERT INTO ai_pipeline.authoring_files (
                session_id, filename, file_type, file_size_bytes,
                storage_path, uploaded_by
            ) VALUES (
                %s, %s, %s, %s, %s, %s
            ) RETURNING file_id
        """
        try:
            result = AuthoringFilesRepository.fetch_one(query, (
                session_id, filename, file_type, file_size_bytes,
                storage_path, uploaded_by
            ))
            return result['file_id'] if result else None
        except Exception as e:
            logger.error(f"Error creating file record: {e}")
            return None

    @staticmethod
    def get_file_by_id(file_id: str) -> Optional[Dict]:
        """Get file record by ID"""
        query = """
            SELECT
                file_id, session_id, filename, file_type,
                file_size_bytes, storage_path,
                extracted_text, extracted_metadata,
                analysis_status, ai_analysis_id, processing_error,
                uploaded_by, uploaded_at, created_at
            FROM ai_pipeline.authoring_files
            WHERE file_id = %s
        """
        try:
            return AuthoringFilesRepository.fetch_one(query, (file_id,))
        except Exception as e:
            logger.error(f"Error fetching file: {e}")
            return None

    @staticmethod
    def get_files_by_session(session_id: str) -> List[Dict]:
        """
        Get all files for a session.

        Args:
            session_id: UUID of authoring session

        Returns:
            List of file records
        """
        query = """
            SELECT
                file_id, filename, file_type, file_size_bytes,
                storage_path, analysis_status,
                extracted_text IS NOT NULL as has_extracted_text,
                uploaded_by, uploaded_at
            FROM ai_pipeline.authoring_files
            WHERE session_id = %s
            ORDER BY uploaded_at ASC
        """
        try:
            return AuthoringFilesRepository.fetch_all(query, (session_id,))
        except Exception as e:
            logger.error(f"Error fetching session files: {e}")
            return []

    @staticmethod
    def update_extracted_content(
        file_id: str,
        extracted_text: str,
        extracted_metadata: Dict
    ) -> bool:
        """
        Update extracted content from file.

        Args:
            file_id: UUID of file
            extracted_text: Extracted text content
            extracted_metadata: Metadata (page count, etc.)

        Returns:
            True if successful
        """
        query = """
            UPDATE ai_pipeline.authoring_files
            SET extracted_text = %s,
                extracted_metadata = %s,
                analysis_status = 'completed'
            WHERE file_id = %s
        """
        try:
            AuthoringFilesRepository.execute_update(
                query,
                (extracted_text, extracted_metadata, file_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error updating extracted content: {e}")
            return False

    @staticmethod
    def update_analysis_status(
        file_id: str,
        status: str,
        ai_analysis_id: Optional[str] = None,
        error: Optional[str] = None
    ) -> bool:
        """
        Update file analysis status.

        Args:
            file_id: UUID of file
            status: Analysis status
            ai_analysis_id: Optional analysis ID
            error: Optional error message

        Returns:
            True if successful
        """
        query = """
            UPDATE ai_pipeline.authoring_files
            SET analysis_status = %s,
                ai_analysis_id = %s,
                processing_error = %s
            WHERE file_id = %s
        """
        try:
            AuthoringFilesRepository.execute_update(
                query,
                (status, ai_analysis_id, error, file_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error updating analysis status: {e}")
            return False

    @staticmethod
    def delete_file(file_id: str) -> bool:
        """
        Delete file record.

        Args:
            file_id: UUID of file

        Returns:
            True if successful
        """
        query = "DELETE FROM ai_pipeline.authoring_files WHERE file_id = %s"
        try:
            AuthoringFilesRepository.execute_update(query, (file_id,))
            return True
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False

    @staticmethod
    def get_files_by_status(
        session_id: str,
        status: str
    ) -> List[Dict]:
        """
        Get files by analysis status.

        Args:
            session_id: UUID of authoring session
            status: Analysis status

        Returns:
            List of file records
        """
        query = """
            SELECT
                file_id, filename, file_type, file_size_bytes,
                storage_path, analysis_status, processing_error,
                uploaded_at
            FROM ai_pipeline.authoring_files
            WHERE session_id = %s AND analysis_status = %s
            ORDER BY uploaded_at ASC
        """
        try:
            return AuthoringFilesRepository.fetch_all(query, (session_id, status))
        except Exception as e:
            logger.error(f"Error fetching files by status: {e}")
            return []

    @staticmethod
    def get_session_file_statistics(session_id: str) -> Dict:
        """
        Get file statistics for session.

        Args:
            session_id: UUID of authoring session

        Returns:
            Statistics dict
        """
        query = """
            SELECT
                COUNT(*) as total_files,
                SUM(file_size_bytes) as total_size_bytes,
                COUNT(CASE WHEN analysis_status = 'completed' THEN 1 END) as completed,
                COUNT(CASE WHEN analysis_status = 'pending' THEN 1 END) as pending,
                COUNT(CASE WHEN analysis_status = 'processing' THEN 1 END) as processing,
                COUNT(CASE WHEN analysis_status = 'failed' THEN 1 END) as failed
            FROM ai_pipeline.authoring_files
            WHERE session_id = %s
        """
        try:
            result = AuthoringFilesRepository.fetch_one(query, (session_id,))
            return result if result else {
                'total_files': 0,
                'total_size_bytes': 0,
                'completed': 0,
                'pending': 0,
                'processing': 0,
                'failed': 0
            }
        except Exception as e:
            logger.error(f"Error fetching file statistics: {e}")
            return {
                'total_files': 0,
                'total_size_bytes': 0,
                'completed': 0,
                'pending': 0,
                'processing': 0,
                'failed': 0
            }

    @staticmethod
    def get_files_for_analysis(session_id: str) -> List[Dict]:
        """
        Get all completed files ready for analysis.

        Args:
            session_id: UUID of authoring session

        Returns:
            List of file records with extracted content
        """
        query = """
            SELECT
                file_id, filename, file_type,
                extracted_text, extracted_metadata,
                uploaded_at
            FROM ai_pipeline.authoring_files
            WHERE session_id = %s
            AND analysis_status = 'completed'
            AND extracted_text IS NOT NULL
            ORDER BY uploaded_at ASC
        """
        try:
            return AuthoringFilesRepository.fetch_all(query, (session_id,))
        except Exception as e:
            logger.error(f"Error fetching files for analysis: {e}")
            return []
