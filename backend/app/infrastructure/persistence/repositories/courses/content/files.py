"""
LernsystemX Course File Repository

Manages course file attachments and media associations.
Supports PDF scripts, supplementary materials, and AI processing.

Phase: C2.x - Course Files Management
ISO 9001:2015 compliant - Standardized data access
"""

from typing import Optional, List, Dict, Any
from uuid import UUID

from app.infrastructure.persistence.repositories.core.base import BaseRepository
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query


class CourseFileRepository(BaseRepository):
    """
    Repository for course file management

    Handles CRUD operations for course_files table including:
    - File uploads and metadata
    - Category-based organisation (script, material, exercise, etc.)
    - AI processing status tracking
    - Download counting
    """

    table_name = 'courses.course_files'
    pk_column = 'course_file_id'

    @classmethod
    def find_by_course(
        cls,
        course_id: str,
        category: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all files for a course, optionally filtered by category

        Args:
            course_id: UUID of the course
            category: Optional category filter (script, material, exercise, etc.)
            limit: Maximum number of records
            offset: Number of records to skip

        Returns:
            List of course files ordered by order_index
        """
        query = """
            SELECT
                cf.*,
                mf.public_url,
                mf.cdn_url,
                mf.status as media_status,
                COALESCE(u.full_name, u.email) as uploader_name
            FROM courses.course_files cf
            LEFT JOIN billing_storage.media_files mf ON cf.file_id = mf.file_id
            LEFT JOIN core.users u ON cf.uploaded_by = u.user_id
            WHERE cf.course_id = %s
        """
        params: List[Any] = [course_id]

        if category:
            query += " AND cf.file_category = %s"
            params.append(category)

        query += " ORDER BY cf.order_index ASC, cf.created_at ASC"

        if limit:
            query += f" LIMIT {limit}"
        if offset:
            query += f" OFFSET {offset}"

        return fetch_all(query, tuple(params))

    @classmethod
    def count_by_course(cls, course_id: str, category: Optional[str] = None) -> int:
        """
        Count files for a course

        Args:
            course_id: UUID of the course
            category: Optional category filter

        Returns:
            Number of files
        """
        query = "SELECT COUNT(*) FROM courses.course_files WHERE course_id = %s"
        params: List[Any] = [course_id]

        if category:
            query += " AND file_category = %s"
            params.append(category)

        result = fetch_one(query, tuple(params))
        return result['count'] if result else 0

    @classmethod
    def get_categories_summary(cls, course_id: str) -> List[Dict[str, Any]]:
        """
        Get file count per category for a course

        Args:
            course_id: UUID of the course

        Returns:
            List of {category, count} dictionaries
        """
        query = """
            SELECT
                file_category,
                COUNT(*) as count,
                SUM(file_size_bytes) as total_size
            FROM courses.course_files
            WHERE course_id = %s
            GROUP BY file_category
            ORDER BY file_category
        """
        return fetch_all(query, (course_id,))

    @classmethod
    def create_file(
        cls,
        course_id: str,
        file_name: str,
        file_type: str,
        uploaded_by: str,
        file_size_bytes: Optional[int] = None,
        mime_type: Optional[str] = None,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        file_category: str = 'material',
        storage_path: Optional[str] = None,
        external_url: Optional[str] = None,
        file_id: Optional[str] = None,
        is_public: bool = False,
        requires_enrollment: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new course file entry

        Args:
            course_id: UUID of the course
            file_name: Original filename
            file_type: File type (pdf, docx, etc.)
            uploaded_by: UUID of the uploader
            file_size_bytes: File size in bytes
            mime_type: MIME type
            display_name: Display name (defaults to file_name)
            description: Optional description
            file_category: Category (script, material, exercise, etc.)
            storage_path: Internal storage path
            external_url: External URL (S3, CDN)
            file_id: Link to media_files table
            is_public: Whether file is publicly accessible
            requires_enrollment: Whether enrollment is required to download

        Returns:
            Created course file record
        """
        # Get next order index
        next_order = cls._get_next_order_index(course_id, file_category)

        data = {
            'course_id': course_id,
            'file_name': file_name,
            'file_type': file_type,
            'file_size_bytes': file_size_bytes,
            'mime_type': mime_type,
            'display_name': display_name or file_name,
            'description': description,
            'file_category': file_category,
            'order_index': next_order,
            'storage_path': storage_path,
            'external_url': external_url,
            'file_id': file_id,
            'uploaded_by': uploaded_by,
            'is_public': is_public,
            'requires_enrollment': requires_enrollment,
            'processed_for_ai': False
        }

        return cls.create(data)

    @classmethod
    def _get_next_order_index(cls, course_id: str, file_category: str) -> int:
        """Get next order index for a course's files in a category"""
        query = """
            SELECT COALESCE(MAX(order_index), -1) + 1 as next_index
            FROM courses.course_files
            WHERE course_id = %s AND file_category = %s
        """
        result = fetch_one(query, (course_id, file_category))
        return result['next_index'] if result else 0

    @classmethod
    def update_order(cls, course_id: str, file_ids: List[str]) -> bool:
        """
        Update order of files for a course

        Args:
            course_id: UUID of the course
            file_ids: List of file IDs in new order

        Returns:
            True if successful
        """
        for idx, file_id in enumerate(file_ids):
            query = """
                UPDATE courses.course_files
                SET order_index = %s, updated_at = NOW()
                WHERE course_file_id = %s AND course_id = %s
            """
            execute_query(query, (idx, file_id, course_id))

        return True

    @classmethod
    def increment_download_count(cls, course_file_id: str) -> Optional[Dict[str, Any]]:
        """
        Increment download count for a file

        Args:
            course_file_id: UUID of the course file

        Returns:
            Updated record
        """
        query = """
            UPDATE courses.course_files
            SET download_count = download_count + 1, updated_at = NOW()
            WHERE course_file_id = %s
            RETURNING *
        """
        return fetch_one(query, (course_file_id,))

    @classmethod
    def mark_ai_processed(
        cls,
        course_file_id: str,
        extracted_text: Optional[str] = None,
        summary: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Mark file as processed by AI and store extracted content

        Args:
            course_file_id: UUID of the course file
            extracted_text: Full extracted text
            summary: AI-generated summary

        Returns:
            Updated record
        """
        query = """
            UPDATE courses.course_files
            SET
                processed_for_ai = TRUE,
                ai_extracted_text = %s,
                ai_summary = %s,
                updated_at = NOW()
            WHERE course_file_id = %s
            RETURNING *
        """
        return fetch_one(query, (extracted_text, summary, course_file_id))

    @classmethod
    def get_unprocessed_files(cls, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get files that haven't been processed by AI

        Args:
            limit: Maximum number of files to return

        Returns:
            List of unprocessed files
        """
        query = """
            SELECT cf.*, c.title as course_title
            FROM courses.course_files cf
            JOIN courses.courses c ON cf.course_id = c.course_id
            WHERE cf.processed_for_ai = FALSE
            AND cf.file_type IN ('pdf', 'docx', 'pptx', 'txt')
            ORDER BY cf.created_at ASC
            LIMIT %s
        """
        return fetch_all(query, (limit,))

    @classmethod
    def get_public_files(cls, course_id: str) -> List[Dict[str, Any]]:
        """
        Get all public files for a course (no enrollment required)

        Args:
            course_id: UUID of the course

        Returns:
            List of public files
        """
        return cls.find_all_by(
            course_id=course_id,
            is_public=True,
            order_by='order_index ASC'
        )

    @classmethod
    def delete_by_course(cls, course_id: str) -> int:
        """
        Delete all files for a course (used when deleting course)

        Args:
            course_id: UUID of the course

        Returns:
            Number of deleted files
        """
        query = """
            DELETE FROM courses.course_files
            WHERE course_id = %s
            RETURNING course_file_id
        """
        results = fetch_all(query, (course_id,))
        return len(results) if results else 0

    @classmethod
    def find_existing_duplicate(
        cls,
        course_id: str,
        original_name: str,
        size_bytes: int
    ) -> Optional[Dict[str, Any]]:
        """
        Check if a duplicate file already exists for a course.

        A file is considered a duplicate if it has the same course_id,
        original file name (case-insensitive), and file size.

        Args:
            course_id: UUID of the course
            original_name: Original filename (case-insensitive comparison)
            size_bytes: File size in bytes

        Returns:
            Existing file record if duplicate found, None otherwise
        """
        query = """
            SELECT *
            FROM courses.course_files
            WHERE course_id = %s
            AND LOWER(file_name) = LOWER(%s)
            AND file_size_bytes = %s
            LIMIT 1
        """
        return fetch_one(query, (course_id, original_name, size_bytes))
