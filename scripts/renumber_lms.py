#!/usr/bin/env python3
"""
Renumber Learning Methods from lm00-lm25 (with gaps) to lm00-lm18 (continuous)
"""

import os
import json
import re
from pathlib import Path

# Mapping: OLD → NEW
RENUMBER_MAP = {
    'lm00': 'lm00',  # Gruppe A
    'lm01': 'lm01',
    'lm02': 'lm02',
    'lm03': 'lm03',
    'lm06': 'lm04',
    'lm08': 'lm05',  # Gruppe B
    'lm12': 'lm06',
    'lm13': 'lm07',
    'lm14': 'lm08',
    'lm15': 'lm09',
    'lm17': 'lm10',
    'lm18': 'lm11',  # Gruppe C
    'lm19': 'lm12',
    'lm20': 'lm13',
    'lm21': 'lm14',
    'lm22': 'lm15',
    'lm23': 'lm16',
    'lm24': 'lm17',
    'lm25': 'lm18'
}

# Reverse map for file renaming (to avoid conflicts)
REVERSE_MAP = {v: k for k, v in RENUMBER_MAP.items()}

BASE_DIR = Path('/home/pascal/Lernsystem')
FRONTEND = BASE_DIR / 'frontend/src'


def renumber_json_keys(file_path: Path):
    """Renumber LM keys in JSON file."""
    print(f"  Processing: {file_path.relative_to(BASE_DIR)}")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Renumber keys
    new_data = {}
    for old_key, value in data.items():
        new_key = RENUMBER_MAP.get(old_key, old_key)
        new_data[new_key] = value

    # Sort by new keys (lm00-lm18)
    sorted_data = {k: new_data[k] for k in sorted(new_data.keys())}

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=2)

    print(f"    ✓ Renumbered {len(data)} → {len(sorted_data)} keys")


def renumber_vue_files():
    """Rename LearningMethodXXForm.vue files."""
    print("\n📝 Renaming Vue Form files...")

    forms_dir = FRONTEND / 'components/desktop/windows/learning-methods'

    # Create temp mapping to avoid conflicts
    temp_files = {}

    # Step 1: Rename to temp names
    for old_id, new_id in RENUMBER_MAP.items():
        old_file = forms_dir / f'LearningMethod{old_id[2:]}.vue'
        if old_file.exists() and old_id != new_id:
            temp_file = forms_dir / f'LearningMethod{old_id[2:]}_TEMP.vue'
            old_file.rename(temp_file)
            temp_files[new_id] = temp_file
            print(f"  {old_file.name} → {temp_file.name}")

    # Step 2: Rename temp to final names
    for new_id, temp_file in temp_files.items():
        final_file = forms_dir / f'LearningMethod{new_id[2:]}Form.vue'
        temp_file.rename(final_file)
        print(f"  {temp_file.name} → {final_file.name}")

    print(f"  ✓ Renamed {len(temp_files)} Vue files")


def update_vue_method_codes():
    """Update METHOD_CODE constants in Vue files."""
    print("\n🔧 Updating METHOD_CODE in Vue files...")

    forms_dir = FRONTEND / 'components/desktop/windows/learning-methods'

    for new_id in RENUMBER_MAP.values():
        vue_file = forms_dir / f'LearningMethod{new_id[2:]}Form.vue'
        if not vue_file.exists():
            continue

        content = vue_file.read_text(encoding='utf-8')

        # Update METHOD_CODE = XX
        new_code = int(new_id[2:])
        content = re.sub(
            r'const METHOD_CODE = \d+',
            f'const METHOD_CODE = {new_code}',
            content
        )

        vue_file.write_text(content, encoding='utf-8')
        print(f"  ✓ {vue_file.name}: METHOD_CODE = {new_code}")


def update_backend_mapping():
    """Update backend learning_method_mapping.py."""
    print("\n🐍 Updating backend learning_method_mapping.py...")

    mapping_file = BASE_DIR / 'backend/app/ki/learning_method_mapping.py'
    content = mapping_file.read_text(encoding='utf-8')

    # Replace all lmXX references in the file
    for old_id, new_id in RENUMBER_MAP.items():
        if old_id != new_id:
            # Replace in comments and strings
            content = re.sub(rf'\b{old_id}\b', new_id, content)

    mapping_file.write_text(content, encoding='utf-8')
    print("  ✓ Updated backend mapping")


def create_db_migration():
    """Create SQL migration for renumbering."""
    print("\n💾 Creating DB migration...")

    migrations_dir = BASE_DIR / 'backend/migrations'

    # Find next migration number
    existing = sorted([f for f in migrations_dir.glob('*.sql')])
    if existing:
        last_num = int(existing[-1].name[:3])
        next_num = last_num + 1
    else:
        next_num = 67

    migration_file = migrations_dir / f'{next_num:03d}_renumber_learning_methods.sql'

    sql = """-- Renumber Learning Methods from lm00-lm25 (with gaps) to lm00-lm18 (continuous)
-- This removes gaps in numbering for cleaner system architecture

BEGIN;

-- Update learning_method_types table
-- Map old method_type values to new continuous numbering

"""

    # Create UPDATE statements
    updates = []
    for old_id, new_id in RENUMBER_MAP.items():
        old_num = int(old_id[2:])
        new_num = int(new_id[2:])
        if old_num != new_num:
            updates.append(f"-- {old_id} → {new_id}")
            updates.append(
                f"UPDATE learning_method_types SET method_type = {new_num} "
                f"WHERE method_type = {old_num};"
            )
            updates.append(
                f"UPDATE learning_method_instances SET method_type = {new_num} "
                f"WHERE method_type = {old_num};"
            )
            updates.append("")

    sql += "\n".join(updates)
    sql += "\nCOMMIT;\n"

    migration_file.write_text(sql, encoding='utf-8')
    print(f"  ✓ Created {migration_file.name}")


def main():
    print("="*70)
    print("🔢 RENUMBERING LEARNING METHODS: lm00-lm25 → lm00-lm18")
    print("="*70)

    # 1. Renumber i18n keys in JSON files
    print("\n📚 Renumbering i18n keys...")
    for lang in ['de', 'en', 'pl']:
        lm_file = FRONTEND / f'locales/{lang}/windows/learningMethods.json'
        if lm_file.exists():
            renumber_json_keys(lm_file)

    # 2. Rename Vue files
    renumber_vue_files()

    # 3. Update METHOD_CODE constants
    update_vue_method_codes()

    # 4. Update backend mapping
    update_backend_mapping()

    # 5. Create DB migration
    create_db_migration()

    print("\n" + "="*70)
    print("✅ RENUMBERING COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("1. Run: cd backend && python setup/migrations.py")
    print("2. Run: cd frontend && npm run build")
    print("3. Verify all 19 LMs work correctly")


if __name__ == '__main__':
    main()
