"""Media Repository"""
from typing import Optional
from src.infrastructure.database.connection import get_db_connection
from src.api.media.core.domain.entities.media_file import MediaFile

class MediaRepository:
    @staticmethod
    def find_by_id(file_id: str) -> Optional[MediaFile]:
        query = "SELECT * FROM media.media_files WHERE file_id = %s"
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (file_id,))
                row = cur.fetchone()
                if not row:
                    return None
                return MediaFile(
                    file_id=str(row[0]), user_id=str(row[1]), file_name=row[2],
                    file_path=row[3], file_type=row[4], file_size=row[5],
                    mime_type=row[6], duration=row[7], created_at=row[8]
                )
