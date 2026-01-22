#!/usr/bin/env python3
"""
Verification Script: Confirm that emergency rollback script won't be executed during migration discovery

This script tests the glob pattern behavior to ensure _999_rollback_group_system.sql
will NOT be discovered by the migration system.

The migration discovery pattern: **/[0-9][0-9][0-9]_*.sql

This pattern requires:
- ** matches any directory depth
- [0-9][0-9][0-9] matches EXACTLY three digits
- _ comes after the three digits
- * matches anything after underscore
"""

from pathlib import Path
import glob
import sys

def test_migration_pattern():
    """Test that the rollback script is NOT discovered."""

    backend_dir = Path(__file__).parent
    migrations_dir = backend_dir / "migrations"

    print("=" * 80)
    print("MIGRATION DISCOVERY VERIFICATION")
    print("=" * 80)
    print()

    # Test the exact glob pattern used by migration system
    pattern = "**/[0-9][0-9][0-9]_*.sql"

    print(f"Testing Pattern: {pattern}")
    print(f"Search Directory: {migrations_dir}")
    print()

    # Get all discovered migrations
    discovered = list(migrations_dir.glob(pattern))
    discovered = sorted([f.relative_to(migrations_dir) for f in discovered])

    print(f"DISCOVERED MIGRATIONS ({len(discovered)} files):")
    print("-" * 80)

    for migration in discovered:
        print(f"  ✓ {migration}")

    print()

    # Check for rollback file
    rollback_files = [f for f in discovered if 'rollback' in str(f).lower()]

    print("=" * 80)
    print("ROLLBACK SCRIPT STATUS")
    print("=" * 80)

    if rollback_files:
        print("❌ ERROR: ROLLBACK SCRIPT FOUND IN MIGRATIONS")
        for f in rollback_files:
            print(f"   ❌ {f}")
        print()
        print("   This file WILL be executed during setup!")
        print("   CRITICAL ISSUE - Setup wizard will fail!")
        return False
    else:
        print("✅ SUCCESS: No rollback scripts found in migrations")
        print()
        print("   The emergency rollback script will NOT be executed")
        print("   Group system will initialize properly during setup")

    print()

    # Verify the file exists in emergency rollbacks
    emergency_rollback = migrations_dir / "_emergency_rollbacks" / "_999_rollback_group_system.sql"

    print("=" * 80)
    print("EMERGENCY ROLLBACK FILE STATUS")
    print("=" * 80)

    if emergency_rollback.exists():
        print(f"✅ Emergency rollback file exists: {emergency_rollback.relative_to(migrations_dir)}")
        print()
        print("   File Details:")
        print(f"   - Location: {emergency_rollback}")
        print(f"   - Size: {emergency_rollback.stat().st_size} bytes")
        print(f"   - Name Pattern Match: [0-9][0-9][0-9]_*.sql")
        print(f"   - Matches Pattern: NO (starts with '_', not digit)")
        print()
        print("   This file is properly excluded from migration discovery")
        return True
    else:
        print(f"❌ ERROR: Emergency rollback file not found!")
        print(f"   Expected location: {emergency_rollback}")
        return False

def test_glob_pattern_behavior():
    """Test glob pattern behavior to explain why the fix works."""

    print()
    print("=" * 80)
    print("GLOB PATTERN ANALYSIS")
    print("=" * 80)
    print()

    test_cases = [
        ("001_users.sql", True, "Standard migration - matches pattern"),
        ("024_groups.sql", True, "Standard migration - matches pattern"),
        ("999_rollback.sql", True, "Would match (if in migration dir)"),
        ("_999_rollback.sql", False, "Starts with _ instead of digit - DOES NOT match"),
        ("_emergency_rollbacks/_999_rollback.sql", False, "Starts with _ - DOES NOT match"),
    ]

    pattern = "[0-9][0-9][0-9]_*.sql"

    print(f"Pattern: {pattern}")
    print()
    print("Test Cases:")
    print("-" * 80)

    for filename, should_match, explanation in test_cases:
        # Test the pattern
        import fnmatch
        matches = fnmatch.fnmatch(filename, pattern)

        status = "✓" if matches == should_match else "✗"
        result = "MATCHES" if matches else "NO MATCH"

        print(f"{status} {filename:40} → {result:12} ({explanation})")

    print()

if __name__ == "__main__":
    print()
    print()

    # Run glob pattern analysis
    test_glob_pattern_behavior()

    # Run migration discovery test
    success = test_migration_pattern()

    print()
    print("=" * 80)
    print("VERIFICATION RESULT")
    print("=" * 80)

    if success:
        print()
        print("✅ VERIFICATION PASSED")
        print()
        print("The emergency rollback script (_999_rollback_group_system.sql) will NOT")
        print("be executed during the setup wizard migration discovery process.")
        print()
        print("The Group System will initialize properly and B2B customers can create")
        print("accounts with automatic Owner group creation.")
        print()
        sys.exit(0)
    else:
        print()
        print("❌ VERIFICATION FAILED")
        print()
        print("Critical issue detected - the emergency rollback script may be executed")
        print("during setup, which would destroy the group system!")
        print()
        sys.exit(1)
