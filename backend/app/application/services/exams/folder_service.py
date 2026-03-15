"""
Folder Service — Business logic for archive folder management.

DDD Layer: Application (use cases)
"""
import logging
from typing import Dict, List, Optional

from app.infrastructure.persistence.repositories.exams.folders import ArchiveFolderRepository
from app.infrastructure.persistence.repositories.exams.programs import ExamProgramRepository

logger = logging.getLogger(__name__)

MAX_FOLDER_DEPTH = 20


class FolderService:
    """Orchestrates folder CRUD with business rule enforcement."""

    @staticmethod
    def list_programs_with_root_folders() -> List[Dict]:
        """Get all exam programs with their root folder counts."""
        programs = ExamProgramRepository.find_all()
        for prog in programs:
            roots = ArchiveFolderRepository.find_children(
                parent_folder_id=None, program_id=prog['program_id']
            )
            prog['root_folder_count'] = len(roots)
            prog['total_file_count'] = sum(r.get('file_count', 0) for r in roots)
        return programs

    @staticmethod
    def get_folder_contents(folder_id: str) -> Optional[Dict]:
        """Get a folder's metadata, children folders, and files."""
        folder = ArchiveFolderRepository.find_by_id(folder_id)
        if not folder:
            return None

        children = ArchiveFolderRepository.find_children(parent_folder_id=folder_id)
        files = ArchiveFolderRepository.find_files_in_folder(folder_id)
        breadcrumb = ArchiveFolderRepository.find_breadcrumb(folder_id)

        return {
            'folder': folder,
            'children': children,
            'files': files,
            'breadcrumb': breadcrumb,
        }

    @staticmethod
    def get_program_root_contents(program_id: int) -> Dict:
        """Get root-level folders for a program."""
        children = ArchiveFolderRepository.find_children(
            parent_folder_id=None, program_id=program_id
        )
        return {
            'folder': None,
            'children': children,
            'files': [],
            'breadcrumb': [],
        }

    @staticmethod
    def get_sidebar_tree(program_id: int) -> List[Dict]:
        """Get full folder tree for sidebar display."""
        flat = ArchiveFolderRepository.find_tree_for_program(program_id)
        return _build_nested_tree(flat)

    @staticmethod
    def create_folder(program_id: int, name: str,
                      parent_folder_id: Optional[str] = None,
                      icon: Optional[str] = None,
                      user_id: Optional[str] = None) -> Dict:
        """Create a new folder with validation."""
        if parent_folder_id:
            parent = ArchiveFolderRepository.find_by_id(parent_folder_id)
            if not parent:
                raise ValueError("Parent folder not found")
            program_id = parent['program_id']

            breadcrumb = ArchiveFolderRepository.find_breadcrumb(parent_folder_id)
            if len(breadcrumb) >= MAX_FOLDER_DEPTH:
                raise ValueError(f"Maximum folder depth ({MAX_FOLDER_DEPTH}) reached")

        folder = ArchiveFolderRepository.create(
            program_id=program_id,
            name=name,
            parent_folder_id=parent_folder_id,
            icon=icon,
            created_by=user_id,
        )
        logger.info("Created folder '%s' (id=%s) under program %s",
                     name, folder['folder_id'], program_id)
        return folder

    @staticmethod
    def rename_folder(folder_id: str, new_name: str) -> Optional[Dict]:
        """Rename a folder."""
        return ArchiveFolderRepository.update(folder_id, name=new_name)

    @staticmethod
    def update_folder(folder_id: str, **kwargs) -> Optional[Dict]:
        """Update folder fields (name, icon, metadata)."""
        return ArchiveFolderRepository.update(folder_id, **kwargs)

    @staticmethod
    def move_folder(folder_id: str,
                    new_parent_id: Optional[str]) -> Optional[Dict]:
        """Move a folder to a new parent with circular reference protection."""
        result = ArchiveFolderRepository.move(folder_id, new_parent_id)
        if result is None:
            raise ValueError("Move blocked: circular reference or folder not found")
        logger.info("Moved folder %s -> parent %s", folder_id, new_parent_id)
        return result

    @staticmethod
    def delete_folder(folder_id: str) -> bool:
        """Delete a folder and all descendants (exams get folder_id=NULL)."""
        deleted = ArchiveFolderRepository.delete(folder_id)
        if deleted:
            logger.info("Deleted folder %s and descendants", folder_id)
        return deleted

    @staticmethod
    def move_file_to_folder(exam_id: str, folder_id: Optional[str]) -> bool:
        """Move an exam/file into a folder."""
        from app.infrastructure.persistence.repositories.exams.core import ExamRepository
        return ExamRepository.update_exam(
            exam_id, {'folder_id': folder_id}
        )


def _build_nested_tree(flat_rows: List[Dict]) -> List[Dict]:
    """Convert flat CTE result into nested tree structure."""
    by_id = {}
    roots = []
    for row in flat_rows:
        row['children'] = []
        by_id[str(row['folder_id'])] = row

    for row in flat_rows:
        parent_id = str(row['parent_folder_id']) if row.get('parent_folder_id') else None
        if parent_id and parent_id in by_id:
            by_id[parent_id]['children'].append(row)
        else:
            roots.append(row)

    return roots
