"""
Archive Folder Repository — CRUD for hierarchical folder structure.

DDD Layer: Infrastructure (persistence)
Table: assessments.archive_folders
"""
import logging
from typing import Any, Dict, List, Optional

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, execute_query,
)

logger = logging.getLogger(__name__)


class ArchiveFolderRepository:
    """Repository for archive_folders table — unlimited nesting under exam_programs."""

    @staticmethod
    def find_by_id(folder_id: str) -> Optional[Dict[str, Any]]:
        """Get a single folder by ID."""
        return fetch_one("""
            SELECT folder_id, parent_folder_id, program_id, name, icon,
                   position, metadata, created_by, created_at, updated_at
            FROM assessments.archive_folders
            WHERE folder_id = %s
        """, (folder_id,))

    @staticmethod
    def find_children(parent_folder_id: Optional[str] = None,
                      program_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get direct children of a folder, or root folders for a program."""
        conditions: list[str] = []
        params: list = []

        conditions: list[str] = ["f.trashed_at IS NULL"]
        if parent_folder_id:
            conditions.append("f.parent_folder_id = %s")
            params.append(parent_folder_id)
        else:
            conditions.append("f.parent_folder_id IS NULL")

        if program_id:
            conditions.append("f.program_id = %s")
            params.append(program_id)

        where = " AND ".join(conditions)

        return fetch_all(f"""
            SELECT f.folder_id, f.parent_folder_id, f.program_id, f.name, f.icon,
                   f.position, f.metadata, f.created_at,
                   (SELECT COUNT(*) FROM assessments.archive_folders c
                    WHERE c.parent_folder_id = f.folder_id AND c.trashed_at IS NULL) AS child_count,
                   (SELECT COUNT(*) FROM assessments.exams e
                    WHERE e.folder_id = f.folder_id) AS file_count
            FROM assessments.archive_folders f
            WHERE {where}
            ORDER BY f.position, f.name
        """, tuple(params))

    @staticmethod
    def find_tree_for_program(program_id: int) -> List[Dict[str, Any]]:
        """Get entire folder tree for a program using recursive CTE."""
        return fetch_all("""
            WITH RECURSIVE folder_tree AS (
                SELECT folder_id, parent_folder_id, name, icon, position, 0 AS depth
                FROM assessments.archive_folders
                WHERE program_id = %s AND parent_folder_id IS NULL AND trashed_at IS NULL
                UNION ALL
                SELECT f.folder_id, f.parent_folder_id, f.name, f.icon, f.position,
                       ft.depth + 1
                FROM assessments.archive_folders f
                JOIN folder_tree ft ON f.parent_folder_id = ft.folder_id
                WHERE f.trashed_at IS NULL
            )
            SELECT ft.*,
                   (SELECT COUNT(*) FROM assessments.archive_folders c
                    WHERE c.parent_folder_id = ft.folder_id) AS child_count,
                   (SELECT COUNT(*) FROM assessments.exams e
                    WHERE e.folder_id = ft.folder_id) AS file_count
            FROM folder_tree ft
            ORDER BY ft.depth, ft.position, ft.name
        """, (program_id,))

    @staticmethod
    def create(program_id: int, name: str,
               parent_folder_id: Optional[str] = None,
               icon: Optional[str] = None,
               created_by: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Create a new folder. Returns the created folder."""
        if parent_folder_id:
            pos_row = fetch_one("""
                SELECT COALESCE(MAX(position), -1) + 1 AS next_pos
                FROM assessments.archive_folders
                WHERE parent_folder_id = %s
            """, (parent_folder_id,))
        else:
            pos_row = fetch_one("""
                SELECT COALESCE(MAX(position), -1) + 1 AS next_pos
                FROM assessments.archive_folders
                WHERE program_id = %s AND parent_folder_id IS NULL
            """, (program_id,))
        next_pos = pos_row['next_pos'] if pos_row else 0

        return fetch_one("""
            INSERT INTO assessments.archive_folders
                (program_id, parent_folder_id, name, icon, position, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING folder_id, parent_folder_id, program_id, name, icon,
                      position, metadata, created_at
        """, (program_id, parent_folder_id, name, icon, next_pos, created_by))

    @staticmethod
    def update(folder_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update folder fields (name, icon, position, metadata)."""
        allowed = {'name', 'icon', 'position', 'metadata', 'parent_folder_id'}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return None

        set_clause = ", ".join(f"{k} = %s" for k in updates)
        params = tuple(list(updates.values()) + [folder_id])

        return fetch_one(f"""
            UPDATE assessments.archive_folders
            SET {set_clause}, updated_at = NOW()
            WHERE folder_id = %s
            RETURNING folder_id, parent_folder_id, program_id, name, icon,
                      position, metadata, updated_at
        """, params)

    @staticmethod
    def trash(folder_id: str) -> bool:
        """Soft-delete a folder (move to trash)."""
        result = fetch_one("""
            UPDATE assessments.archive_folders
            SET trashed_at = NOW()
            WHERE folder_id = %s AND trashed_at IS NULL
            RETURNING folder_id
        """, (folder_id,))
        # Also trash all descendants
        if result:
            execute_query("""
                WITH RECURSIVE descendants AS (
                    SELECT folder_id FROM assessments.archive_folders
                    WHERE parent_folder_id = %s
                    UNION ALL
                    SELECT f.folder_id FROM assessments.archive_folders f
                    JOIN descendants d ON f.parent_folder_id = d.folder_id
                )
                UPDATE assessments.archive_folders
                SET trashed_at = NOW()
                WHERE folder_id IN (SELECT folder_id FROM descendants)
                  AND trashed_at IS NULL
            """, (folder_id,))
        return result is not None

    @staticmethod
    def restore(folder_id: str) -> bool:
        """Restore a folder from trash."""
        result = fetch_one("""
            UPDATE assessments.archive_folders
            SET trashed_at = NULL
            WHERE folder_id = %s AND trashed_at IS NOT NULL
            RETURNING folder_id
        """, (folder_id,))
        # Also restore descendants
        if result:
            execute_query("""
                WITH RECURSIVE descendants AS (
                    SELECT folder_id FROM assessments.archive_folders
                    WHERE parent_folder_id = %s
                    UNION ALL
                    SELECT f.folder_id FROM assessments.archive_folders f
                    JOIN descendants d ON f.parent_folder_id = d.folder_id
                )
                UPDATE assessments.archive_folders
                SET trashed_at = NULL
                WHERE folder_id IN (SELECT folder_id FROM descendants)
            """, (folder_id,))
        return result is not None

    @staticmethod
    def purge(folder_id: str) -> bool:
        """Permanently delete a trashed folder."""
        result = fetch_one("""
            DELETE FROM assessments.archive_folders
            WHERE folder_id = %s AND trashed_at IS NOT NULL
            RETURNING folder_id
        """, (folder_id,))
        return result is not None

    @staticmethod
    def find_trashed() -> List[Dict[str, Any]]:
        """Get all trashed folders (for trash view)."""
        return fetch_all("""
            SELECT f.folder_id, f.name, f.icon, f.program_id, f.trashed_at,
                   p.display_name AS program_name
            FROM assessments.archive_folders f
            LEFT JOIN assessments.exam_programs p ON p.program_id = f.program_id
            WHERE f.trashed_at IS NOT NULL
            ORDER BY f.trashed_at DESC
        """)

    @staticmethod
    def move(folder_id: str, new_parent_id: Optional[str]) -> Optional[Dict[str, Any]]:
        """Move a folder to a new parent. Validates no circular reference."""
        if new_parent_id:
            circular = fetch_one("""
                WITH RECURSIVE ancestors AS (
                    SELECT folder_id, parent_folder_id
                    FROM assessments.archive_folders
                    WHERE folder_id = %s
                    UNION ALL
                    SELECT f.folder_id, f.parent_folder_id
                    FROM assessments.archive_folders f
                    JOIN ancestors a ON f.folder_id = a.parent_folder_id
                )
                SELECT folder_id FROM ancestors WHERE folder_id = %s
            """, (new_parent_id, folder_id))
            if circular:
                logger.warning("Circular reference blocked: %s -> %s",
                               folder_id, new_parent_id)
                return None

        return fetch_one("""
            UPDATE assessments.archive_folders
            SET parent_folder_id = %s, updated_at = NOW()
            WHERE folder_id = %s
            RETURNING folder_id, parent_folder_id, name
        """, (new_parent_id, folder_id))

    @staticmethod
    def find_breadcrumb(folder_id: str) -> List[Dict[str, Any]]:
        """Get breadcrumb path from root to this folder."""
        return fetch_all("""
            WITH RECURSIVE path AS (
                SELECT folder_id, parent_folder_id, name, icon, program_id, 0 AS depth
                FROM assessments.archive_folders WHERE folder_id = %s
                UNION ALL
                SELECT f.folder_id, f.parent_folder_id, f.name, f.icon, f.program_id,
                       p.depth + 1
                FROM assessments.archive_folders f
                JOIN path p ON f.folder_id = p.parent_folder_id
            )
            SELECT folder_id, name, icon, program_id
            FROM path ORDER BY depth DESC
        """, (folder_id,))

    @staticmethod
    def find_files_in_folder(folder_id: str) -> List[Dict[str, Any]]:
        """Get exams/files in a folder with analysis status."""
        return fetch_all("""
            SELECT e.exam_id, e.title, e.pdf_path, e.analysis_status,
                   e.created_at, e.year, e.season, e.part,
                   (SELECT COUNT(*) FROM assessments.exam_questions q
                    WHERE q.exam_id = e.exam_id) AS question_count
            FROM assessments.exams e
            WHERE e.folder_id = %s
            ORDER BY e.title, e.created_at
        """, (folder_id,))

    @staticmethod
    def find_files_in_folder_recursive(folder_id: str) -> List[Dict[str, Any]]:
        """Get exams/files in a folder AND all subfolders (recursive)."""
        return fetch_all("""
            WITH RECURSIVE subtree AS (
                SELECT folder_id FROM assessments.archive_folders
                WHERE folder_id = %s
                UNION ALL
                SELECT f.folder_id FROM assessments.archive_folders f
                JOIN subtree s ON f.parent_folder_id = s.folder_id
                WHERE f.trashed_at IS NULL
            )
            SELECT e.exam_id, e.title, e.pdf_path, e.analysis_status,
                   e.created_at, e.year, e.season, e.part,
                   (SELECT COUNT(*) FROM assessments.exam_questions q
                    WHERE q.exam_id = e.exam_id) AS question_count
            FROM assessments.exams e
            WHERE e.folder_id IN (SELECT folder_id FROM subtree)
            ORDER BY e.title, e.created_at
        """, (folder_id,))
