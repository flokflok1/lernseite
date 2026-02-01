"""
Learning Method Groups Repository

Data access layer for learning method groups (A, B, C, etc.)
Now database-driven - no hardcoding!

Groups are master data that define the categories of learning methods.
"""

from typing import Dict, Any, Optional, List
import psycopg
from psycopg.rows import dict_row

from app.core.bootstrap import extensions


class LearningMethodGroupRepository:
    """
    Repository for Learning Method Groups.
    
    Manages access to learning_method_groups table.
    All groups are stored in database - fully flexible.
    """
    
    @classmethod
    def find_all(cls) -> List[Dict[str, Any]]:
        """
        Get all active learning method groups.

        Returns:
            List of group dicts sorted by sort_order
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT
                        group_code,
                        name,
                        description,
                        icon,
                        tier,
                        sort_order,
                        is_active,
                        created_at
                    FROM learning_methods.learning_method_groups
                    WHERE is_active = TRUE
                    ORDER BY sort_order, group_code
                """)
                return cur.fetchall()
    
    @classmethod
    def find_by_code(cls, group_code: str) -> Optional[Dict[str, Any]]:
        """
        Find a group by code.

        Args:
            group_code: Single letter group code (A, B, C, etc.)

        Returns:
            Group dict or None if not found
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT
                        group_code,
                        name,
                        description,
                        icon,
                        tier,
                        sort_order,
                        is_active
                    FROM learning_methods.learning_method_groups
                    WHERE group_code = %s
                """, (group_code,))
                return cur.fetchone()
    
    @classmethod
    def get_icon_for_group(cls, group_code: str) -> Optional[str]:
        """
        Get the icon for a group (for UI display).
        
        Args:
            group_code: Group code (A, B, C, etc.)
            
        Returns:
            Icon string or None
        """
        group = cls.find_by_code(group_code)
        return group.get('icon') if group else None
    
    @classmethod
    def get_name_for_group(cls, group_code: str) -> Optional[str]:
        """
        Get the display name for a group.

        Args:
            group_code: Group code (A, B, C, etc.)

        Returns:
            Group name or None
        """
        group = cls.find_by_code(group_code)
        return group.get('name') if group else None

    @classmethod
    def get_tier_for_group(cls, group_code: str) -> Optional[str]:
        """
        Get the tier level for a group (database-driven, not hardcoded!).

        Args:
            group_code: Group code (A, B, C, etc.)

        Returns:
            Tier (basic, premium, enterprise) or None if not found
        """
        group = cls.find_by_code(group_code)
        return group.get('tier') if group else None
    
    @classmethod
    def create_group(cls,
                     group_code: str,
                     name: str,
                     description: str = "",
                     icon: str = "",
                     sort_order: int = 0,
                     tier: str = "basic") -> Dict[str, Any]:
        """
        Create a new group.

        Args:
            group_code: Single letter code
            name: Display name
            description: Full description
            icon: Icon/emoji
            sort_order: Display order
            tier: Tier level (basic, premium, enterprise) - default basic

        Returns:
            Created group dict
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    INSERT INTO learning_methods.learning_method_groups
                    (group_code, name, description, icon, sort_order, tier, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, TRUE)
                    RETURNING *
                """, (group_code, name, description, icon, sort_order, tier))

                conn.commit()
                return cur.fetchone()
    
    @classmethod
    def update_group(cls, group_code: str, **updates) -> Optional[Dict[str, Any]]:
        """
        Update a group.

        Args:
            group_code: Group code
            **updates: Fields to update (name, description, icon, sort_order, is_active, tier)

        Returns:
            Updated group dict or None
        """
        allowed_fields = ['name', 'description', 'icon', 'sort_order', 'is_active', 'tier']
        update_fields = []
        params = []

        for field in allowed_fields:
            if field in updates:
                update_fields.append(f"{field} = %s")
                params.append(updates[field])

        if not update_fields:
            return cls.find_by_code(group_code)

        params.append(group_code)

        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                query = f"""
                    UPDATE learning_methods.learning_method_groups
                    SET {', '.join(update_fields)}
                    WHERE group_code = %s
                    RETURNING *
                """
                cur.execute(query, params)
                conn.commit()
                return cur.fetchone()
    
    @classmethod
    def get_icons_map(cls) -> Dict[str, str]:
        """
        Get mapping of all group codes to icons.
        
        Useful for UI to quickly access icons.
        
        Returns:
            Dict mapping group_code -> icon
        """
        groups = cls.find_all()
        return {group['group_code']: group['icon'] for group in groups}
    
    @classmethod
    def get_names_map(cls) -> Dict[str, str]:
        """
        Get mapping of all group codes to names.
        
        Returns:
            Dict mapping group_code -> name
        """
        groups = cls.find_all()
        return {group['group_code']: group['name'] for group in groups}
