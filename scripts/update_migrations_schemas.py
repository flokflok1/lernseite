#!/usr/bin/env python3
"""
Update all Migration Files to use Schema-Qualified Table Names

This script updates all SQL migration files to use PostgreSQL schema prefixes.

Example:
    CREATE TABLE users         → CREATE TABLE core.users
    REFERENCES courses(...)    → REFERENCES courses.courses(...)
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

# Base directory
BASE_DIR = Path('/home/pascal/Lernsystem')
MIGRATIONS_DIR = BASE_DIR / 'backend/migrations'

# TABLE → SCHEMA MAPPING (same as repository update)
TABLE_SCHEMA_MAP = {
    # CORE SCHEMA
    'users': 'core',
    'roles': 'core',
    'permissions': 'core',
    'role_permissions': 'core',
    'user_sessions': 'core',
    'user_preferences': 'core',
    'system_settings': 'core',
    'audit_logs': 'core',
    'recovery_codes': 'core',
    'api_versions': 'core',

    # ORGANISATIONS SCHEMA
    'organisations': 'organisations',
    'organisation_members': 'organisations',
    'organisation_classes': 'organisations',
    'organisation_settings': 'organisations',
    'organisation_token_pools': 'organisations',

    # COURSES SCHEMA
    'courses': 'courses',
    'course_categories': 'courses',
    'chapters': 'courses',
    'modules': 'courses',  # Alias
    'lessons': 'courses',
    'enrollments': 'courses',
    'course_enrollments': 'courses',
    'course_access': 'courses',
    'course_prompts': 'courses',
    'course_files': 'courses',
    'course_authoring_sessions': 'courses',
    'course_ai_settings': 'courses',
    'chapter_theory': 'courses',
    'lesson_videos': 'courses',
    'lesson_explanations': 'courses',

    # LEARNING_METHODS SCHEMA
    'learning_method_types': 'learning_methods',
    'learning_method_instances': 'learning_methods',
    'learning_method_progress': 'learning_methods',
    'lm_ai_flashcards': 'learning_methods',
    'lm_ai_diagrams': 'learning_methods',
    'lm_ai_scenarios': 'learning_methods',
    'lm_ai_step_by_step': 'learning_methods',
    'lm_ai_theory': 'learning_methods',
    'lm_ai_whiteboard': 'learning_methods',
    'lm_ai_math': 'learning_methods',
    'lm_ai_lab': 'learning_methods',
    'lm_ai_open_questions': 'learning_methods',
    'lm_ai_exam_sim': 'learning_methods',
    'authoring_actions': 'learning_methods',
    'lm_model_routing': 'learning_methods',
    'capability_slots': 'learning_methods',
    'math_toolkit': 'learning_methods',

    # ASSESSMENTS SCHEMA
    'exams': 'assessments',
    'exam_questions': 'assessments',
    'exam_results': 'assessments',
    'exam_question_pool': 'assessments',
    'exam_simulations': 'assessments',
    'exam_simulation_sessions': 'assessments',
    'exam_simulation_results': 'assessments',
    'certificates': 'assessments',
    'certificate_progress': 'assessments',

    # AI_PIPELINE SCHEMA
    'ai_providers': 'ai_pipeline',
    'ai_models': 'ai_pipeline',
    'ai_model_profiles': 'ai_pipeline',
    'prompts': 'ai_pipeline',
    'prompt_templates': 'ai_pipeline',
    'ki_requests': 'ai_pipeline',
    'ki_jobs': 'ai_pipeline',
    'ai_jobs': 'ai_pipeline',
    'ki_raw_inputs': 'ai_pipeline',
    'ai_authoring_studio': 'ai_pipeline',
    'ai_generation_history': 'ai_pipeline',

    # LIVEROOM SCHEMA
    'rooms': 'liveroom',
    'liverooms': 'liveroom',
    'room_participants': 'liveroom',
    'room_settings': 'liveroom',
    'room_whiteboards': 'liveroom',
    'room_whiteboard_items': 'liveroom',
    'whiteboard_recognition_cache': 'liveroom',
    'room_transcripts': 'liveroom',
    'room_recordings': 'liveroom',
    'room_ai_stats': 'liveroom',

    # ANALYTICS SCHEMA
    'learning_events': 'analytics',
    'learning_sessions': 'analytics',
    'user_activity_logs': 'analytics',
    'dashboards': 'analytics',
    'dashboard_widgets': 'analytics',
    'widget_registry': 'analytics',
    'feedback_system': 'analytics',
    'feedback_responses': 'analytics',
    'daily_aggregations': 'analytics',
    'weekly_aggregations': 'analytics',
    'monthly_aggregations': 'analytics',

    # SMART_AGENTS SCHEMA
    'course_agents': 'smart_agents',
    'agent_knowledge_base': 'smart_agents',
    'agent_cache': 'smart_agents',
    'agent_query_logs': 'smart_agents',
    'organisation_agent_extensions': 'smart_agents',
    'agent_media_cache': 'smart_agents',

    # SUPPORT_SYSTEMS SCHEMA
    'notifications': 'support_systems',
    'notification_preferences': 'support_systems',
    'groups': 'support_systems',
    'group_members': 'support_systems',
    'group_resources': 'support_systems',
    'badges': 'support_systems',
    'user_badges': 'support_systems',
    'xp_system': 'support_systems',
    'streaks': 'support_systems',
    'leaderboards': 'support_systems',
    'messages': 'support_systems',
    'message_threads': 'support_systems',

    # BILLING_STORAGE SCHEMA
    'subscriptions': 'billing_storage',
    'subscription_plans': 'billing_storage',
    'invoices': 'billing_storage',
    'payment_methods': 'billing_storage',
    'token_wallets': 'billing_storage',
    'token_transactions': 'billing_storage',
    'token_packages': 'billing_storage',
    'media_files': 'billing_storage',
    'media_versions': 'billing_storage',
    'storage_quotas': 'billing_storage',

    # TRANSLATIONS SCHEMA
    'translations': 'translations',
    'translation_suggestions': 'translations',
    'i18n_config': 'translations',
    'pronunciation_overrides': 'translations',
}


def update_migration_file(file_path: Path) -> Tuple[int, List[str]]:
    """
    Update a single migration file with schema-qualified table names.

    Returns:
        (changes_count, change_descriptions)
    """
    # Skip 001_core_users_roles.sql - already manually updated
    if file_path.name == '001_core_users_roles.sql':
        return (0, ['Skipped - already updated manually'])

    # Read file
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    changes = []

    # Pattern 1: CREATE TABLE tablename → CREATE TABLE schema.tablename
    def replace_create_table(match):
        exists = match.group(1)  # IF NOT EXISTS or empty
        table = match.group(2)

        # Skip if already schema-qualified
        if '.' in table:
            return match.group(0)

        schema = TABLE_SCHEMA_MAP.get(table.lower())
        if schema:
            changes.append(f"CREATE TABLE: {table} → {schema}.{table}")
            return f"CREATE TABLE {exists}{schema}.{table}"
        return match.group(0)

    content = re.sub(
        r'CREATE\s+TABLE\s+(IF\s+NOT\s+EXISTS\s+)?(\w+)',
        replace_create_table,
        content,
        flags=re.IGNORECASE
    )

    # Pattern 2: REFERENCES tablename → REFERENCES schema.tablename
    def replace_references(match):
        table = match.group(1)
        rest = match.group(2)

        if '.' in table:
            return match.group(0)

        schema = TABLE_SCHEMA_MAP.get(table.lower())
        if schema:
            changes.append(f"REFERENCES: {table} → {schema}.{table}")
            return f"REFERENCES {schema}.{table}{rest}"
        return match.group(0)

    content = re.sub(
        r'REFERENCES\s+(\w+)(\([^)]+\))',
        replace_references,
        content,
        flags=re.IGNORECASE
    )

    # Pattern 3: FROM/JOIN/UPDATE/INSERT INTO/DELETE FROM
    sql_keywords = [
        r'FROM\s+',
        r'JOIN\s+',
        r'UPDATE\s+',
        r'INSERT\s+INTO\s+',
        r'DELETE\s+FROM\s+'
    ]

    for keyword in sql_keywords:
        pattern = rf'({keyword})(\w+)(\s+(?:WHERE|ON|SET|VALUES|AS|\w{{1,3}}|LEFT|RIGHT|INNER|OUTER|CROSS|\(|$))'

        def replace_keyword(match):
            prefix = match.group(1)
            table = match.group(2)
            suffix = match.group(3)

            if '.' in table:
                return match.group(0)

            # Skip SQL keywords
            skip_words = {
                'WHERE', 'ON', 'SET', 'VALUES', 'AS', 'AND', 'OR', 'NOT',
                'NULL', 'TRUE', 'FALSE', 'LIMIT', 'OFFSET', 'ORDER', 'GROUP',
                'LEFT', 'RIGHT', 'INNER', 'OUTER', 'CROSS', 'FULL', 'NATURAL'
            }
            if table.upper() in skip_words:
                return match.group(0)

            schema = TABLE_SCHEMA_MAP.get(table.lower())
            if schema:
                changes.append(f"{keyword.strip()}: {table} → {schema}.{table}")
                return f"{prefix}{schema}.{table}{suffix}"
            return match.group(0)

        content = re.sub(pattern, replace_keyword, content, flags=re.IGNORECASE | re.MULTILINE)

    # Pattern 4: INDEX ON tablename → INDEX ON schema.tablename
    def replace_index(match):
        prefix = match.group(1)
        table = match.group(2)
        rest = match.group(3)

        if '.' in table:
            return match.group(0)

        schema = TABLE_SCHEMA_MAP.get(table.lower())
        if schema:
            changes.append(f"INDEX ON: {table} → {schema}.{table}")
            return f"{prefix}{schema}.{table}{rest}"
        return match.group(0)

    content = re.sub(
        r'(INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?[\w]+\s+ON\s+)(\w+)(\()',
        replace_index,
        content,
        flags=re.IGNORECASE
    )

    # Pattern 5: COMMENT ON TABLE tablename → COMMENT ON TABLE schema.tablename
    def replace_comment(match):
        table = match.group(1)
        rest = match.group(2)

        if '.' in table:
            return match.group(0)

        schema = TABLE_SCHEMA_MAP.get(table.lower())
        if schema:
            changes.append(f"COMMENT ON TABLE: {table} → {schema}.{table}")
            return f"COMMENT ON TABLE {schema}.{table}{rest}"
        return match.group(0)

    content = re.sub(
        r'COMMENT\s+ON\s+TABLE\s+(\w+)((?:\s+IS|\.))',
        replace_comment,
        content,
        flags=re.IGNORECASE
    )

    # Write if changed
    if content != original_content:
        file_path.write_text(content, encoding='utf-8')
        return (len(changes), changes)
    else:
        return (0, ['No changes needed'])


def main():
    """Main execution."""
    print("=" * 80)
    print("🔧 UPDATING MIGRATION FILES TO USE SCHEMA-QUALIFIED TABLE NAMES")
    print("=" * 80)

    # Find all migration SQL files
    migration_files = sorted(MIGRATIONS_DIR.glob('**/*.sql'))
    migration_files = [f for f in migration_files if f.is_file() and not f.name.startswith('verify_')]

    print(f"\nFound {len(migration_files)} migration files to process\n")

    total_changes = 0
    updated_files = 0

    # Update each file
    for migration_file in migration_files:
        relative_path = migration_file.relative_to(MIGRATIONS_DIR)

        change_count, change_list = update_migration_file(migration_file)

        if change_count > 0:
            print(f"📝 {relative_path}")
            for change in change_list[:5]:  # Show first 5 changes
                print(f"  ✓ {change}")
            if len(change_list) > 5:
                print(f"  ... and {len(change_list) - 5} more changes")
            total_changes += change_count
            updated_files += 1
        else:
            print(f"→ {relative_path} - {change_list[0]}")

    print("\n" + "=" * 80)
    print("✅ MIGRATION UPDATE COMPLETE!")
    print("=" * 80)
    print(f"\nStatistics:")
    print(f"  Files processed: {len(migration_files)}")
    print(f"  Files updated: {updated_files}")
    print(f"  Total changes: {total_changes}")
    print("\nNext steps:")
    print("1. Review changes: git diff backend/migrations/")
    print("2. Test migrations: python setup/migrations.py")
    print("3. Run Setup Wizard to build fresh DB")


if __name__ == '__main__':
    main()
