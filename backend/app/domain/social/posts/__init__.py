"""
Posts Domain - User Posts System

Components:
- post_manager.py - Post CRUD operations
- media_handler.py - Media attachment handling
- post_types.py - Different post types
- draft_manager.py - Draft posts
"""

from app.domain.social.posts.post_manager import PostManager

__all__ = ['PostManager']
