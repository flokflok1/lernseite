"""
Authoring File Service — Application Layer

Orchestrates file upload, listing, deletion, and text extraction
for AI authoring sessions. DDD-compliant: uses repositories for DB
access and PDFService for extraction.
"""

import os
import logging
from typing import Dict, List, Optional
from flask import current_app
from werkzeug.utils import secure_filename

from app.infrastructure.persistence.repositories.authoring.files import (
    AuthoringFilesRepository,
)

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'ppt', 'pptx',
    'xls', 'xlsx', 'txt', 'png', 'jpg', 'jpeg',
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def _get_extension(filename: str) -> str:
    return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''


def _get_upload_dir(session_id: str) -> str:
    base = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    return os.path.join(base, 'authoring', session_id)


class AuthoringFileService:
    """Application service for authoring file operations."""

    @staticmethod
    def upload_file(
        session_id: str,
        file_obj,
        filename: str,
        user_id: str,
    ) -> Dict:
        """
        Upload a file for an authoring session.

        Validates extension/size, saves to disk, creates DB record,
        and triggers PDF extraction if applicable.
        """
        ext = _get_extension(filename)
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"File type .{ext} not allowed. "
                f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

        # Read content and check size
        file_content = file_obj.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise ValueError(
                f"File too large ({len(file_content)} bytes). "
                f"Max: {MAX_FILE_SIZE // (1024 * 1024)} MB"
            )

        # Save to disk
        upload_dir = _get_upload_dir(session_id)
        os.makedirs(upload_dir, exist_ok=True)

        safe_name = secure_filename(filename)
        storage_path = os.path.join(upload_dir, safe_name)

        # Avoid overwriting existing files
        counter = 1
        base_name, base_ext = os.path.splitext(safe_name)
        while os.path.exists(storage_path):
            safe_name = f"{base_name}_{counter}{base_ext}"
            storage_path = os.path.join(upload_dir, safe_name)
            counter += 1

        with open(storage_path, 'wb') as f:
            f.write(file_content)

        # Create DB record
        file_id = AuthoringFilesRepository.create_file(
            session_id=session_id,
            filename=filename,
            file_type=ext,
            file_size_bytes=len(file_content),
            storage_path=storage_path,
            uploaded_by=user_id,
        )

        if not file_id:
            # Clean up saved file on DB failure
            if os.path.exists(storage_path):
                os.remove(storage_path)
            raise RuntimeError("Failed to create file record in database")

        # Extract text for PDFs
        analysis_status = 'pending'
        if ext == 'pdf':
            analysis_status = AuthoringFileService._extract_pdf(
                file_id, file_content, filename
            )

        return {
            'file_id': file_id,
            'filename': filename,
            'file_type': ext,
            'file_size_bytes': len(file_content),
            'analysis_status': analysis_status,
        }

    @staticmethod
    def _extract_pdf(file_id: str, content: bytes, filename: str) -> str:
        """Extract text from PDF and update DB. Returns final status."""
        try:
            AuthoringFilesRepository.update_analysis_status(
                file_id, 'processing'
            )
            from app.application.services.content.pdf import PDFService
            result = PDFService.extract_text(content, filename)
            AuthoringFilesRepository.update_extracted_content(
                file_id,
                result['extracted_text'],
                result.get('extracted_metadata', {}),
            )
            return 'completed'
        except Exception as e:
            logger.error(f"PDF extraction failed for {filename}: {e}")
            AuthoringFilesRepository.update_analysis_status(
                file_id, 'failed', error=str(e)
            )
            return 'failed'

    @staticmethod
    def list_files(session_id: str) -> List[Dict]:
        """List all files for a session."""
        return AuthoringFilesRepository.get_files_by_session(session_id)

    @staticmethod
    def delete_file(session_id: str, file_id: str) -> bool:
        """Delete a file from disk and database."""
        file_record = AuthoringFilesRepository.get_file_by_id(file_id)
        if not file_record:
            return False

        # Verify file belongs to this session
        if str(file_record.get('session_id')) != str(session_id):
            return False

        # Remove from disk
        storage_path = file_record.get('storage_path')
        if storage_path and os.path.exists(storage_path):
            try:
                os.remove(storage_path)
            except OSError as e:
                logger.warning(f"Failed to delete file from disk: {e}")

        return AuthoringFilesRepository.delete_file(file_id)

    @staticmethod
    def get_extracted_content(
        session_id: str, file_id: str
    ) -> Optional[Dict]:
        """Get extracted text content for a file."""
        record = AuthoringFilesRepository.get_file_by_id(file_id)
        if not record:
            return None
        if str(record.get('session_id')) != str(session_id):
            return None
        return {
            'file_id': file_id,
            'filename': record.get('filename'),
            'extracted_text': record.get('extracted_text', ''),
            'analysis_status': record.get('analysis_status'),
        }
