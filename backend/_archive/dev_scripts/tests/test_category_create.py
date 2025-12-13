"""Test category creation directly"""
import os
from dotenv import load_dotenv
load_dotenv()

from app.repositories.category_repository import CategoryRepository

# Test creating a root category
test_data = {
    'name': 'Test Category',
    'slug': 'test-category',
    'description': 'Test',
    'parent_id': None,
    'level': 1,
    'icon': '📚',
    'color': '#3B82F6',
    'order_index': 0,
    'is_active': True
}

try:
    print("Creating test category...")
    result = CategoryRepository.create(test_data)
    print("✅ Success!")
    print(f"Category created with ID: {result['category_id']}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
