"""
LernsystemX Setup - Seed Data - Course Categories

Seeds initial data for 8 course categories:
- Programming, Languages, Business, Science
- Mathematics, History, Art & Design, Technology

Continuation of config.py (split for Quality Gate G01: max 500 lines per file).

For system features, see: config.py
For learning methods and user roles, see:
- seeds.py: Core seeding functions
- seeds_roles.py: User roles

ISO 9001:2015 compliant - Data standardization
"""

from typing import Dict, List, Optional
from datetime import datetime

from app.infrastructure.persistence.database.connection import fetch_one, execute_query, insert_returning


class SeedDataConfigCategories:
    """
    Seed course category data

    Provides predefined data for 8 course categories.
    """

    @classmethod
    def seed_categories(cls, skip_existing: bool = True) -> int:
        """
        Seed 8 course categories

        Categories:
        - Programming
        - Languages
        - Business
        - Science
        - Mathematics
        - History
        - Art & Design
        - Technology

        Args:
            skip_existing: Skip if categories already exist

        Returns:
            Number of categories created

        Example:
            >>> count = SeedDataConfigCategories.seed_categories()
            >>> print(f"Created {count} course categories")
        """
        # Check if categories already exist
        if skip_existing:
            existing = fetch_one("SELECT COUNT(*) FROM courses.course_categories")
            if existing and existing['count'] > 0:
                return 0

        categories = [
            {
                'category_name': 'Programming',
                'description': 'Software development and programming languages',
                'icon': 'code',
                'color': '#FF6B6B',
                'display_order': 1,
                'is_active': True
            },
            {
                'category_name': 'Languages',
                'description': 'Foreign language learning and linguistics',
                'icon': 'globe',
                'color': '#4ECDC4',
                'display_order': 2,
                'is_active': True
            },
            {
                'category_name': 'Business',
                'description': 'Business management, economics, and entrepreneurship',
                'icon': 'briefcase',
                'color': '#45B7D1',
                'display_order': 3,
                'is_active': True
            },
            {
                'category_name': 'Science',
                'description': 'Natural sciences, physics, chemistry, and biology',
                'icon': 'flask',
                'color': '#96CEB4',
                'display_order': 4,
                'is_active': True
            },
            {
                'category_name': 'Mathematics',
                'description': 'Mathematics, calculus, algebra, and statistics',
                'icon': 'calculator',
                'color': '#FFEAA7',
                'display_order': 5,
                'is_active': True
            },
            {
                'category_name': 'History',
                'description': 'Historical events, cultures, and world history',
                'icon': 'book',
                'color': '#DDA15E',
                'display_order': 6,
                'is_active': True
            },
            {
                'category_name': 'Art & Design',
                'description': 'Visual arts, graphic design, and creative skills',
                'icon': 'palette',
                'color': '#BC6C25',
                'display_order': 7,
                'is_active': True
            },
            {
                'category_name': 'Technology',
                'description': 'IT infrastructure, networks, and emerging technologies',
                'icon': 'cpu',
                'color': '#6C63FF',
                'display_order': 8,
                'is_active': True
            }
        ]

        created = 0
        for category in categories:
            try:
                result = execute_query(
                    """
                    INSERT INTO courses.course_categories (
                        category_name, description, icon, color, display_order,
                        is_active, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (category_name) DO NOTHING
                    RETURNING *
                    """,
                    (
                        category['category_name'],
                        category['description'],
                        category['icon'],
                        category['color'],
                        category['display_order'],
                        category['is_active']
                    ),
                    fetch_one=True
                )
                if result:
                    created += 1
            except Exception as e:
                print(f"Error creating category '{category['category_name']}': {str(e)}")

        return created


# Convenience function
def seed_categories(**kwargs) -> int:
    """Quick function to seed course categories"""
    return SeedDataConfigCategories.seed_categories(**kwargs)
