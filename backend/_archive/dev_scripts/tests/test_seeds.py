#!/usr/bin/env python
"""
Quick test script to manually run seeds and see what happens
"""
import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Set up environment
from dotenv import load_dotenv
load_dotenv()

# Initialize database pool
from app.extensions import init_db_pool
init_db_pool(os.getenv('DATABASE_URL'))

# Import and run seeds
from setup.seeds import SeedData

print("=" * 60)
print("TESTING SEED DATA")
print("=" * 60)

# Run seeds with skip_existing=False to force insertion
print("\n1. Running seed_all with skip_existing=False...")
results = SeedData.seed_all(skip_existing=False)

print(f"\nResults:")
print(f"  - Learning Methods: {results['learning_methods']}")
print(f"  - Roles: {results['roles']}")
print(f"  - Categories: {results['categories']}")
print(f"  - Errors: {results.get('errors', [])}")

# Check actual counts in database
print("\n2. Checking database counts...")
from app.database.connection import fetch_one

methods_count = fetch_one("SELECT COUNT(*) as count FROM learning_method_types")
roles_count = fetch_one("SELECT COUNT(*) as count FROM roles")
categories_count = fetch_one("SELECT COUNT(*) as count FROM course_categories")

print(f"\nDatabase Counts:")
print(f"  - Learning Methods in DB: {methods_count['count']}")
print(f"  - Roles in DB: {roles_count['count']}")
print(f"  - Categories in DB: {categories_count['count']}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
