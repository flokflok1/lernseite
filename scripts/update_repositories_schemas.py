#!/usr/bin/env python3
"""
Update all Backend Repositories to use Schema-Qualified Table Names

This script updates all repository files to reference tables with their PostgreSQL schema prefix.

Example:
    table_name = 'users'  →  table_name = 'core.users'
    FROM users            →  FROM core.users
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

# Base directory
BASE_DIR = Path('/home/pascal/Lernsystem')
REPO_DIR = BASE_DIR / 'backend/app/repositories'

# ============================================================================
# TABLE → SCHEMA MAPPING
# ============================================================================

TABLE_SCHEMA_MAP = {
    # CORE SCHEMA
    'users': 'core',
    'roles': 'core',
    'permissions': 'core',
    'role_permissions': 'core',
    'sessions': 'core',
    'user_preferences': 'core',
    'system_settings': 'core',
    'audit_logs': 'core',
    'deprecations': 'core',
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
    'lessons': 'courses',
    'enrollments': 'courses',
    'course_enrollments': 'courses',  # Alias
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
    'liverooms': 'liveroom',  # Alias
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


def update_table_name_attribute(content: str) -> Tuple[str, List[str]]:
    """
    Update table_name class attribute to include schema prefix.

    Example:
        table_name = 'users'  →  table_name = 'core.users'
    """
    changes = []
    pattern = r"table_name\s*=\s*['\"](\w+)['\"]"

    def replacer(match):
        table = match.group(1)
        schema = TABLE_SCHEMA_MAP.get(table)
        if schema:
            changes.append(f"table_name: '{table}' → '{schema}.{table}'")
            return f"table_name = '{schema}.{table}'"
        return match.group(0)

    updated_content = re.sub(pattern, replacer, content)
    return updated_content, changes


def update_manual_queries(content: str) -> Tuple[str, List[str]]:
    """
    Update manual SQL queries to use schema-qualified table names.

    Patterns to match:
    - FROM table_name
    - JOIN table_name
    - UPDATE table_name
    - INSERT INTO table_name
    - DELETE FROM table_name
    """
    changes = []

    # SQL keywords that precede table names
    sql_keywords = [
        r'FROM\s+',
        r'JOIN\s+',
        r'UPDATE\s+',
        r'INSERT\s+INTO\s+',
        r'DELETE\s+FROM\s+'
    ]

    for keyword in sql_keywords:
        # Match: KEYWORD table_name (WHERE/ON/SET/VALUES or alias)
        pattern = rf'({keyword})(\w+)(\s+(?:WHERE|ON|SET|VALUES|AS|\w+|$))'

        def replacer(match):
            prefix = match.group(1)
            table = match.group(2)
            suffix = match.group(3)

            # Skip if already schema-qualified
            if '.' in table:
                return match.group(0)

            # Skip if it's a common SQL keyword/alias
            skip_words = {
                'WHERE', 'ON', 'SET', 'VALUES', 'AS', 'AND', 'OR', 'NOT',
                'NULL', 'TRUE', 'FALSE', 'LIMIT', 'OFFSET', 'ORDER', 'GROUP'
            }
            if table.upper() in skip_words:
                return match.group(0)

            schema = TABLE_SCHEMA_MAP.get(table.lower())
            if schema:
                changes.append(f"SQL: {table} → {schema}.{table}")
                return f"{prefix}{schema}.{table}{suffix}"
            return match.group(0)

        content = re.sub(pattern, replacer, content, flags=re.IGNORECASE | re.MULTILINE)

    return content, changes


def update_repository_file(file_path: Path) -> None:
    """Update a single repository file with schema-qualified table names."""
    print(f"\n📝 Processing: {file_path.name}")

    # Read file
    content = file_path.read_text(encoding='utf-8')
    original_content = content

    # Update table_name attribute
    content, table_changes = update_table_name_attribute(content)

    # Update manual SQL queries
    content, sql_changes = update_manual_queries(content)

    # Check if anything changed
    if content != original_content:
        # Write updated content
        file_path.write_text(content, encoding='utf-8')

        # Print changes
        all_changes = table_changes + sql_changes
        if all_changes:
            for change in all_changes:
                print(f"  ✓ {change}")
        else:
            print(f"  ✓ File updated (formatting only)")
    else:
        print(f"  → No changes needed")


def main():
    """Main execution."""
    print("=" * 80)
    print("🔧 UPDATING BACKEND REPOSITORIES TO USE SCHEMA-QUALIFIED TABLE NAMES")
    print("=" * 80)

    # Find all repository files (exclude __init__.py and base_repository.py)
    repo_files = [
        f for f in REPO_DIR.glob('*.py')
        if f.name not in ['__init__.py', 'base_repository.py']
    ]

    print(f"\nFound {len(repo_files)} repository files to update")

    # Update each file
    for repo_file in sorted(repo_files):
        update_repository_file(repo_file)

    print("\n" + "=" * 80)
    print("✅ REPOSITORY UPDATE COMPLETE!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Review changes: git diff backend/app/repositories/")
    print("2. Test backend: cd backend && python run.py")
    print("3. Run migrations with new schema structure")


if __name__ == '__main__':
    main()
