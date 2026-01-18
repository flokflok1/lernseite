#!/usr/bin/env python3
"""
Split admin.json into logical submodules
"""
import json
from pathlib import Path
from collections import OrderedDict

LOCALES_DIR = Path('.')
LANGUAGES = ['de', 'en', 'pl']

# Define the split strategy
SPLIT_MAP = {
    'users.json': [
        'users', 'userDetail', 'userGroupManagement', 'roles', 'roleStudio'
    ],
    'courses.json': [
        'courses', 'courseDetail', 'courseEditor', 'courseChat',
        'chapters', 'lessons', 'exams'
    ],
    'ai.json': [
        'aiEditor', 'aiSettingsPage', 'prompts', 'methods',
        'learningMethods', 'learning', 'lmRouting'
    ],
    'analytics.json': [
        'analytics', 'analyticsPage'
    ],
    'organisations.json': [
        'organisations', 'org_admin', 'orgDashboardPage', 'orgUsersPage',
        'orgCoursesPage', 'orgSettingsPage', 'orgAnalyticsPage'
    ],
    'system.json': [
        'systemSettings', 'systemFeatures', 'system_admin', 'auditLogs',
        'billing', 'translations', 'i18n', 'plugins'
    ],
    'common.json': [
        'actions', 'nav', 'title', 'dashboard', 'categories'
    ]
}


def sort_json_keys(obj):
    """Recursively sort JSON keys alphabetically."""
    if isinstance(obj, dict):
        return OrderedDict(sorted((k, sort_json_keys(v)) for k, v in obj.items()))
    elif isinstance(obj, list):
        return [sort_json_keys(item) for item in obj]
    else:
        return obj


def split_admin_json(lang: str):
    """Split admin.json for a specific language."""
    admin_file = LOCALES_DIR / lang / 'admin.json'

    # Load admin.json
    with open(admin_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    admin_data = data['admin']

    # Create admin directory
    admin_dir = LOCALES_DIR / lang / 'admin'
    admin_dir.mkdir(exist_ok=True)

    # Split into submodules
    for filename, keys in SPLIT_MAP.items():
        submodule = {}
        for key in keys:
            if key in admin_data:
                submodule[key] = admin_data[key]

        # Sort and save
        sorted_submodule = sort_json_keys(submodule)
        output_file = admin_dir / filename

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sorted_submodule, f, ensure_ascii=False, indent=2)

        print(f"  ✓ Created {lang}/admin/{filename} ({len(submodule)} keys)")

    # Create index.ts barrel export
    index_content = """// Auto-generated barrel export for admin submodules
import users from './users.json'
import courses from './courses.json'
import ai from './ai.json'
import analytics from './analytics.json'
import organisations from './organisations.json'
import system from './system.json'
import common from './common.json'

export default {
  admin: {
    ...users,
    ...courses,
    ...ai,
    ...analytics,
    ...organisations,
    ...system,
    ...common
  }
}
"""

    index_file = admin_dir / 'index.ts'
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content)

    print(f"  ✓ Created {lang}/admin/index.ts")

    # Remove old admin.json
    admin_file.unlink()
    print(f"  ✓ Removed {lang}/admin.json")


def main():
    print("🔧 Splitting admin.json into submodules...\n")

    for lang in LANGUAGES:
        print(f"Processing {lang}...")
        split_admin_json(lang)
        print()

    print("✅ Split complete!")


if __name__ == '__main__':
    main()
