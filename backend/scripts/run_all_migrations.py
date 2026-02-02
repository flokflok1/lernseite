#!/usr/bin/env python3
"""
LernsystemX - Migration Runner
Führt alle SQL-Migrations in der richtigen Reihenfolge aus

EXECUTION ORDER:
  Primary:   Folder order (MIGRATION_DIRS index)
  Secondary: Numeric prefix (000, 001, 002, ...)
  Tertiary:  Filename (lexicographic)

This ensures 01_Core ALWAYS runs before 02_Content, even if both have
migrations with the same numeric prefix (e.g., 008_*.sql).

COLLISION DETECTION:
  Migrations with the same numeric prefix in DIFFERENT folders are flagged
  as potential risks. Set STRICT_MIGRATIONS=1 to fail on collisions.
"""
import os
import glob
import subprocess
import sys
import re
from pathlib import Path
from collections import defaultdict
from typing import List, Tuple, Dict

# Migration directories in correct execution order
# This order is CRITICAL - Core must run before Content, Content before AI, etc.
MIGRATION_DIRS = [
    '01_Core',
    '02_Content',
    '03_AI',
    '04_Analytics',
    '05_Gamification',
    '06_LiveRoom',
    '07_Notifications',
    '08_Storage',
    '09_Billing',
    '10_Community',
    '11_System',
    '12_Social',       # Added missing folder
    '12_Compliance',
    '13_Security',
    '14_Integrations',
    '15_Features',
]

# Build folder index lookup for O(1) access
FOLDER_ORDER = {name: idx for idx, name in enumerate(MIGRATION_DIRS)}


def extract_migration_number(filename: str) -> int:
    """
    Extract numeric prefix from migration filename.

    Examples:
        '000_schemas.sql' -> 0
        '008_courses.sql' -> 8
        'verify_schema.sql' -> 9999 (non-numbered files run last)
    """
    match = re.match(r'^(\d+)_', filename)
    if match:
        return int(match.group(1))
    return 9999  # Non-numbered files run at the end


def get_folder_index(filepath: str) -> int:
    """
    Get the folder order index for a migration file.

    Returns the index from MIGRATION_DIRS, or 9999 for unknown folders.
    This ensures unknown folders run AFTER all known folders.
    """
    parent_dir = Path(filepath).parent.name
    return FOLDER_ORDER.get(parent_dir, 9999)


def get_sort_key(filepath: str) -> Tuple[int, int, str]:
    """
    Generate a deterministic sort key for migration ordering.

    Sort key is (folder_index, migration_number, filename).
    This ensures:
      1. 01_Core always runs before 02_Content
      2. Within a folder, lower numbers run first
      3. Within same number, alphabetical order (deterministic)
    """
    filename = os.path.basename(filepath)
    folder_idx = get_folder_index(filepath)
    migration_num = extract_migration_number(filename)
    return (folder_idx, migration_num, filename)


def detect_collisions(files: List[str]) -> Dict[int, List[str]]:
    """
    Detect migration number collisions across different folders.

    A collision occurs when two migrations in DIFFERENT folders have
    the same numeric prefix. This is dangerous because:

    1. Dependencies: 01_Core/008_*.sql may create tables that
       02_Content/008_*.sql depends on via foreign keys.

    2. Unpredictable order: Without folder-aware sorting, colliding
       migrations could run in undefined order, causing FK failures.

    Returns a dict of {migration_number: [list of colliding files]}
    """
    by_number: Dict[int, List[str]] = defaultdict(list)

    for filepath in files:
        filename = os.path.basename(filepath)
        folder = Path(filepath).parent.name
        migration_num = extract_migration_number(filename)

        # Skip non-numbered files
        if migration_num == 9999:
            continue

        by_number[migration_num].append(f"{folder}/{filename}")

    # Filter to only collisions (same number, different folders)
    collisions = {}
    for num, paths in by_number.items():
        folders = set(p.split('/')[0] for p in paths)
        if len(folders) > 1:  # Multiple folders = collision
            collisions[num] = paths

    return collisions


def print_collision_warnings(collisions: Dict[int, List[str]]) -> None:
    """Print warnings about detected migration number collisions."""
    if not collisions:
        return

    print()
    print('⚠️  COLLISION WARNING: Same migration numbers in different folders')
    print('=' * 70)
    print()
    print('WHY THIS MATTERS:')
    print('  - Migrations may have cross-folder dependencies (e.g., FK references)')
    print('  - Without folder-aware sorting, execution order would be undefined')
    print('  - Current sorting ensures folder order is respected (01_Core → 02_Content)')
    print()
    print('DETECTED COLLISIONS:')

    for num in sorted(collisions.keys()):
        files = collisions[num]
        print(f'  {num:03d}: {len(files)} files')
        for f in sorted(files):
            print(f'       - {f}')

    print()
    print(f'Total: {len(collisions)} collision groups')
    print()
    print('TIP: Consider renumbering migrations to avoid collisions.')
    print('     Set STRICT_MIGRATIONS=1 to fail on collisions.')
    print('=' * 70)
    print()


def get_migration_files() -> List[str]:
    """
    Get all migration files in deterministic execution order.

    Order is determined by:
      1. Folder index (from MIGRATION_DIRS)
      2. Migration number (numeric prefix)
      3. Filename (lexicographic, for determinism)

    This ensures 01_Core ALWAYS completes before 02_Content starts,
    regardless of migration numbers.
    """
    base_path = Path(__file__).parent.parent / 'migrations'
    files = []

    # Collect all .sql files from ordered directories
    for dir_name in MIGRATION_DIRS:
        dir_path = base_path / dir_name
        if dir_path.exists():
            # Include subdirectories (e.g., 11_System/i18n/)
            sql_files = glob.glob(str(dir_path / '**' / '*.sql'), recursive=True)
            files.extend(sql_files)

    # Also check for files directly in migrations/ (e.g., verify_schema.sql)
    direct_files = glob.glob(str(base_path / '*.sql'))
    files.extend(direct_files)

    # Sort with folder-aware key (CRITICAL for correct execution order)
    files.sort(key=get_sort_key)

    return files


def run_migration(filepath: str) -> bool:
    """Run a single migration file."""
    filename = os.path.basename(filepath)
    folder = Path(filepath).parent.name
    display_name = f"{folder}/{filename}"

    print(f'  Running: {display_name}...', end=' ', flush=True)

    try:
        result = subprocess.run(
            ['psql', 'service=devdb', '-f', filepath],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            print('✅')
            return True
        else:
            error_msg = result.stderr[:200] if result.stderr else result.stdout[:200]
            print(f'❌\n    Error: {error_msg}')
            return False

    except subprocess.TimeoutExpired:
        print('❌ Timeout (60s)')
        return False
    except FileNotFoundError:
        print('❌ psql not found - is PostgreSQL client installed?')
        return False
    except Exception as e:
        print(f'❌ {str(e)}')
        return False


def main() -> int:
    """Main entry point."""
    print('=' * 70)
    print('LernsystemX - Migration Runner')
    print('=' * 70)
    print()

    # Check for strict mode
    strict_mode = os.environ.get('STRICT_MIGRATIONS', '0') == '1'
    if strict_mode:
        print('🔒 STRICT MODE: Will fail on migration number collisions')
        print()

    # Get migration files
    files = get_migration_files()

    if not files:
        print('❌ No migration files found!')
        return 1

    print(f'Found {len(files)} migration files')
    print()

    # Detect and report collisions
    collisions = detect_collisions(files)
    if collisions:
        print_collision_warnings(collisions)

        if strict_mode:
            print('❌ STRICT MODE: Failing due to migration number collisions.')
            print('   Fix collisions or unset STRICT_MIGRATIONS to continue.')
            return 1

    # Show execution order preview
    print('Execution order (first 20):')
    for i, f in enumerate(files[:20]):
        folder = Path(f).parent.name
        filename = os.path.basename(f)
        num = extract_migration_number(filename)
        print(f'  {i+1:3d}. [{num:03d}] {folder}/{filename}')
    if len(files) > 20:
        print(f'  ... and {len(files) - 20} more')
    print()

    # Confirm before running
    response = input('Proceed with migration? (y/N): ')
    if response.lower() != 'y':
        print('Aborted.')
        return 0

    print()
    print('Running migrations...')
    print()

    success_count = 0
    failed_count = 0

    for filepath in files:
        if run_migration(filepath):
            success_count += 1
        else:
            failed_count += 1

            # Ask if should continue after failure
            response = input('\n  Continue despite error? (y/N): ')
            if response.lower() != 'y':
                break

    print()
    print('=' * 70)
    print(f'Results: ✅ {success_count} succeeded, ❌ {failed_count} failed')
    print('=' * 70)

    return 0 if failed_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
