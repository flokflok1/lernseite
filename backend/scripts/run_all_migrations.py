#!/usr/bin/env python3
"""
LernsystemX - Migration Runner
Führt alle SQL-Migrations in der richtigen Reihenfolge aus
"""
import os
import glob
import subprocess
import sys
from pathlib import Path

# Migration directories in correct order
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
    '12_Compliance',
    '13_Security',
    '14_Integrations',
    '15_Features',
]

def get_migration_files():
    """Get all migration files in correct order"""
    # Scripts directory is in backend/ root now
    base_path = Path(__file__).parent.parent / 'migrations'
    files = []

    # Get all .sql files from ordered directories
    for dir_name in MIGRATION_DIRS:
        dir_path = base_path / dir_name
        if dir_path.exists():
            sql_files = sorted(glob.glob(str(dir_path / '*.sql')))
            files.extend(sql_files)

    # Also check for files directly in migrations/
    direct_files = sorted(glob.glob(str(base_path / '*.sql')))
    files.extend(direct_files)

    # Sort by migration number (extracted from filename)
    def get_migration_number(filepath):
        filename = os.path.basename(filepath)
        parts = filename.split('_')
        if parts[0].isdigit():
            return int(parts[0])
        return 9999  # Put non-numbered files at end

    files.sort(key=get_migration_number)
    return files

def run_migration(filepath):
    """Run a single migration file"""
    filename = os.path.basename(filepath)
    print(f'  Running: {filename}...', end=' ')

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
            print(f'❌\n    Error: {result.stderr[:200]}')
            return False

    except subprocess.TimeoutExpired:
        print('❌ Timeout')
        return False
    except Exception as e:
        print(f'❌ {str(e)}')
        return False

def main():
    print('=' * 60)
    print('LernsystemX - Migration Runner')
    print('=' * 60)
    print()

    files = get_migration_files()

    if not files:
        print('❌ No migration files found!')
        return 1

    print(f'Found {len(files)} migration files')
    print()

    success_count = 0
    failed_count = 0

    for filepath in files:
        if run_migration(filepath):
            success_count += 1
        else:
            failed_count += 1

            # Ask if should continue
            response = input('\n  Continue? (y/N): ')
            if response.lower() != 'y':
                break

    print()
    print('=' * 60)
    print(f'Results: ✅ {success_count} succeeded, ❌ {failed_count} failed')
    print('=' * 60)

    return 0 if failed_count == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
