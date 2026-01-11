"""Category Repository"""
from typing import Optional, List
from src.infrastructure.database.connection import get_db_connection
from src.api.categories.core.domain.entities.category import Category

class CategoryRepository:
    @staticmethod
    def find_by_id(category_id: int) -> Optional[Category]:
        query = "SELECT * FROM courses.course_categories WHERE category_id = %s"
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (category_id,))
                row = cur.fetchone()
                if not row:
                    return None
                return Category(
                    category_id=row[0], parent_id=row[1], name=row[2], slug=row[3],
                    description=row[4], icon=row[5], color=row[6], level=row[7],
                    order_index=row[8], active=row[9], created_at=row[10], updated_at=row[11],
                    path=row[12] if len(row) > 12 else None,
                    root_id=row[13] if len(row) > 13 else None,
                    path_ids=row[14] if len(row) > 14 else None,
                    name_en=row[15] if len(row) > 15 else None,
                    name_es=row[16] if len(row) > 16 else None,
                    name_fr=row[17] if len(row) > 17 else None,
                    course_count=row[18] if len(row) > 18 else 0,
                    total_course_count=row[19] if len(row) > 19 else 0,
                    meta_title=row[20] if len(row) > 20 else None,
                    meta_description=row[21] if len(row) > 21 else None
                )
    
    @staticmethod
    def list_root_categories() -> List[Category]:
        query = """
        SELECT * FROM courses.course_categories
        WHERE parent_id IS NULL AND active = TRUE
        ORDER BY order_index
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
                cats = []
                for row in rows:
                    cats.append(Category(
                        category_id=row[0], parent_id=row[1], name=row[2], slug=row[3],
                        description=row[4], icon=row[5], color=row[6], level=row[7],
                        order_index=row[8], active=row[9], created_at=row[10], updated_at=row[11]
                    ))
                return cats
    
    @staticmethod
    def list_children(parent_id: int) -> List[Category]:
        query = """
        SELECT * FROM courses.course_categories
        WHERE parent_id = %s AND active = TRUE
        ORDER BY order_index
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (parent_id,))
                rows = cur.fetchall()
                cats = []
                for row in rows:
                    cats.append(Category(
                        category_id=row[0], parent_id=row[1], name=row[2], slug=row[3],
                        description=row[4], icon=row[5], color=row[6], level=row[7],
                        order_index=row[8], active=row[9], created_at=row[10], updated_at=row[11]
                    ))
                return cats
