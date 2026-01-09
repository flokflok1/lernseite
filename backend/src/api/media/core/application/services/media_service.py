"""Media Service"""
from typing import Optional
from src.api.media.core.domain.entities.media_file import MediaFile
from src.api.media.core.infrastructure.repositories.media_repository import MediaRepository

class MediaService:
    @staticmethod
    def get_file(file_id: str) -> Optional[MediaFile]:
        return MediaRepository.find_by_id(file_id)
