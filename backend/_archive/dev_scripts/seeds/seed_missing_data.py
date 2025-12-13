#!/usr/bin/env python
"""
Seed missing data (learning methods and roles)
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from setup.seeds import SeedData

if __name__ == '__main__':
    print("Seeding missing data...")

    try:
        # Skip existing = False to force re-seeding
        result = SeedData.seed_all(skip_existing=False)

        print(f"\n[SUCCESS] Seeding completed:")
        print(f"  - Learning Methods: {result.get('learning_methods', 0)}")
        print(f"  - Roles: {result.get('roles', 0)}")
        print(f"  - Categories: {result.get('categories', 0)}")

    except Exception as e:
        print(f"\n[ERROR] Seeding failed: {e}")
        sys.exit(1)
