"""Repository for storage.pdf_cache table."""

import hashlib
import json
import logging
from typing import Dict, Any, Optional

from app.infrastructure.persistence.database.connection import get_db_connection

logger = logging.getLogger(__name__)


class PDFCacheRepository:
    """CRUD for PDF extraction cache (storage.pdf_cache)."""

    @staticmethod
    def find_by_hash(file_hash: str) -> Optional[Dict[str, Any]]:
        """Find cached PDF extraction by file hash."""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT cache_id, original_filename, extracted_text,
                           extracted_metadata, structure_analysis, page_count
                    FROM storage.pdf_cache
                    WHERE file_hash = %s
                    LIMIT 1
                """, [file_hash])
                row = cur.fetchone()

        if not row:
            return None

        return {
            'cache_id': str(row[0]),
            'original_filename': row[1],
            'extracted_text': row[2],
            'extracted_metadata': row[3] or {},
            'structure_analysis': row[4] or {},
            'page_count': row[5],
        }

    @staticmethod
    def save(
        file_hash: str,
        filename: str,
        extracted_text: str,
        page_count: int,
        file_size_bytes: int,
        processing_time_ms: int,
        metadata: dict = None,
        structure: dict = None,
    ) -> str:
        """Save PDF extraction result. Returns cache_id."""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO storage.pdf_cache
                        (file_hash, original_filename, extracted_text,
                         page_count, file_size_bytes, processing_time_ms,
                         extracted_metadata, structure_analysis)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (file_hash) DO UPDATE SET
                        access_count = storage.pdf_cache.access_count + 1,
                        last_accessed_at = NOW()
                    RETURNING cache_id
                """, [
                    file_hash, filename, extracted_text,
                    page_count, file_size_bytes, processing_time_ms,
                    json.dumps(metadata or {}),
                    json.dumps(structure or {}),
                ])
                result = cur.fetchone()
                conn.commit()
        return str(result[0]) if result else None

    @staticmethod
    def compute_hash(content: bytes) -> str:
        """Compute SHA-256 hash for dedup."""
        return hashlib.sha256(content).hexdigest()
