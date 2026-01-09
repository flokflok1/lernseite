#!/usr/bin/env python3
"""
API Import Update Script - Phase 6

Updates all import statements across the codebase to reflect the new
ISO-compliant directory structure from Phase 5.

Handles 39+ import path changes:
- Admin AI files moved to admin/ai/
- Admin Course files moved to admin/courses/
- Root files moved to domain folders
- tokens.py split into tokens/ package
- math_toolkit.py split into math/ package
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# =============================================================================
# IMPORT MAPPINGS
# =============================================================================

# Format: (old_pattern, new_replacement, description)
IMPORT_MAPPINGS: List[Tuple[str, str, str]] = [
    # -------------------------------------------------------------------------
    # Admin AI Files (10 mappings)
    # -------------------------------------------------------------------------
    (r'from app\.api\.admin_ai_models import', 'from app.api.admin.ai.models import', 'Admin AI Models'),
    (r'from app\.api\.admin_ai_model_profiles import', 'from app.api.admin.ai.model_profiles import', 'Admin AI Model Profiles'),
    (r'from app\.api\.admin_ai_authoring import', 'from app.api.admin.ai.authoring import', 'Admin AI Authoring'),
    (r'from app\.api\.admin_ai_tutor import', 'from app.api.admin.ai.tutor import', 'Admin AI Tutor'),
    (r'from app\.api\.admin_ai_studio([^_])', r'from app.api.admin.ai.studio.core\1', 'Admin AI Studio Core'),
    (r'from app\.api\.admin_ai_studio_chat import', 'from app.api.admin.ai.studio.chat import', 'Admin AI Studio Chat'),
    (r'from app\.api\.admin_ai_studio_generation import', 'from app.api.admin.ai.studio.generation import', 'Admin AI Studio Generation'),
    (r'from app\.api\.admin_ai_studio_sessions import', 'from app.api.admin.ai.studio.sessions import', 'Admin AI Studio Sessions'),
    (r'from app\.api\.admin_ai_studio_variants import', 'from app.api.admin.ai.studio.variants import', 'Admin AI Studio Variants'),
    (r'from app\.api\.admin_ai_studio_utils import', 'from app.api.admin.ai.studio.utils import', 'Admin AI Studio Utils'),

    # -------------------------------------------------------------------------
    # Admin Course Files (4 mappings)
    # -------------------------------------------------------------------------
    (r'from app\.api\.admin_course_ai_settings import', 'from app.api.admin.courses.ai_settings import', 'Admin Course AI Settings'),
    (r'from app\.api\.admin_course_authoring import', 'from app.api.admin.courses.authoring import', 'Admin Course Authoring'),
    (r'from app\.api\.admin_course_system_features import', 'from app.api.admin.courses.system_features import', 'Admin Course System Features'),
    (r'from app\.api\.admin_course_analytics import', 'from app.api.admin.courses.analytics import', 'Admin Course Analytics'),

    # -------------------------------------------------------------------------
    # Admin Other Files (2 mappings)
    # -------------------------------------------------------------------------
    (r'from app\.api\.admin_analytics import', 'from app.api.admin.analytics.system import', 'Admin Analytics'),
    (r'from app\.api\.admin_roles import', 'from app.api.admin.system.roles import', 'Admin Roles'),

    # -------------------------------------------------------------------------
    # Root Files to Domains (13 mappings)
    # -------------------------------------------------------------------------
    (r'from app\.api\.health import', 'from app.api.core.health import', 'Health'),
    (r'from app\.api\.deprecation import', 'from app.api.core.deprecation import', 'Deprecation'),
    (r'from app\.api\.lesson_videos import', 'from app.api.lessons.videos import', 'Lesson Videos'),
    (r'from app\.api\.lesson_explanations import', 'from app.api.lessons.explanations import', 'Lesson Explanations'),
    (r'from app\.api\.tutor([^/])', r'from app.api.tutor.core\1', 'Tutor Core'),
    (r'from app\.api\.analytics([^/])', r'from app.api.analytics.core\1', 'Analytics Core'),
    (r'from app\.api\.feedback([^/])', r'from app.api.feedback.core\1', 'Feedback Core'),
    (r'from app\.api\.audio import', 'from app.api.media.audio import', 'Audio'),
    (r'from app\.api\.org_analytics import', 'from app.api.organisations.analytics import', 'Org Analytics'),
    (r'from app\.api\.auth([^/])', r'from app.api.auth.core\1', 'Auth Core'),
    (r'from app\.api\.dashboard([^/])', r'from app.api.dashboard.core\1', 'Dashboard Core'),
    (r'from app\.api\.categories([^/])', r'from app.api.categories.core\1', 'Categories Core'),
    (r'from app\.api\.chapter_theory([^/])', r'from app.api.chapter_theory.core\1', 'Chapter Theory Core'),
    (r'from app\.api\.learning_methods([^/])', r'from app.api.learning_methods.core\1', 'Learning Methods Core'),

    # -------------------------------------------------------------------------
    # Directory Renames (2 mappings)
    # -------------------------------------------------------------------------
    (r'from app\.api\.exam_simulations\.', 'from app.api.exams.', 'Exams Package'),
    (r'from app\.api\.tts\.', 'from app.api.media.tts.', 'TTS Package'),

    # -------------------------------------------------------------------------
    # Split Files - tokens.py (4 mappings for direct imports)
    # -------------------------------------------------------------------------
    (r'from app\.api\.tokens import (get_my_token_balance|get_organisation_tokens)', r'from app.api.tokens.wallet import \1', 'Tokens Wallet'),
    (r'from app\.api\.tokens import get_my_transactions', 'from app.api.tokens.transactions import get_my_transactions', 'Tokens Transactions'),
    (r'from app\.api\.tokens import (get_my_usage|estimate_ai_cost)', r'from app.api.tokens.stats import \1', 'Tokens Stats'),
    (r'from app\.api\.tokens import (manual_topup|get_token_stats)', r'from app.api.tokens.admin import \1', 'Tokens Admin'),

    # -------------------------------------------------------------------------
    # Split Files - math_toolkit.py (4 mappings for direct imports)
    # -------------------------------------------------------------------------
    (r'from app\.api\.math_toolkit import (get_categories|get_patterns|get_pattern|get_formulas|toggle_formula_favorite|use_formula)', r'from app.api.math.reference import \1', 'Math Reference'),
    (r'from app\.api\.math_toolkit import (evaluate_expression|get_calculator_history|save_calculator_entry)', r'from app.api.math.calculator import \1', 'Math Calculator'),
    (r'from app\.api\.math_toolkit import (start_session|get_session|end_session|get_session_steps|save_session_step)', r'from app.api.math.sessions import \1', 'Math Sessions'),
    (r'from app\.api\.math_toolkit import (get_user_progress|update_user_progress|get_hint|get_tasks|check_task_answer|create_pattern)', r'from app.api.math.interactive import \1', 'Math Interactive'),
]

# Bridge modules to delete after import updates
BRIDGE_MODULES = [
    'admin_learning_methods.py',
    'admin_lm_routing.py',
    'admin_prompts.py',
    'admin_system.py',
    'admin_users.py',
]

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def find_python_files(root_dir: Path) -> List[Path]:
    """Find all Python files in directory tree."""
    python_files = []
    for root, dirs, files in os.walk(root_dir):
        # Skip __pycache__ and .git
        dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git', 'venv', 'node_modules')]
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    return python_files

def update_imports_in_file(file_path: Path, mappings: List[Tuple[str, str, str]]) -> Tuple[int, List[str]]:
    """
    Update import statements in a single file.

    Returns:
        (num_changes, list_of_changes)
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        changes = []

        for old_pattern, new_replacement, description in mappings:
            matches = re.findall(old_pattern, content)
            if matches:
                content = re.sub(old_pattern, new_replacement, content)
                changes.append(f"  - {description}: {len(matches)} replacement(s)")

        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            return len(changes), changes

        return 0, []

    except Exception as e:
        print(f"⚠️  Error processing {file_path}: {e}")
        return 0, []

def delete_bridge_modules(api_dir: Path, bridge_modules: List[str]) -> int:
    """Delete bridge modules."""
    deleted = 0
    for module in bridge_modules:
        module_path = api_dir / module
        if module_path.exists():
            try:
                module_path.unlink()
                print(f"✅ Deleted bridge module: {module}")
                deleted += 1
            except Exception as e:
                print(f"⚠️  Failed to delete {module}: {e}")
        else:
            print(f"ℹ️  Bridge module not found: {module}")
    return deleted

# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main execution."""
    print("=" * 80)
    print("API Import Update Script - Phase 6")
    print("=" * 80)

    # Paths
    backend_dir = Path(__file__).parent
    app_dir = backend_dir / "app"
    api_dir = app_dir / "api"
    setup_dir = backend_dir / "setup"

    if not api_dir.exists():
        print(f"❌ API directory not found: {api_dir}")
        return 1

    print(f"\n📂 Scanning directories:")
    print(f"   - {app_dir}")
    print(f"   - {setup_dir}")

    # Find all Python files
    python_files = []
    python_files.extend(find_python_files(app_dir))
    if setup_dir.exists():
        python_files.extend(find_python_files(setup_dir))

    print(f"\n📊 Found {len(python_files)} Python files")
    print(f"📝 Processing {len(IMPORT_MAPPINGS)} import mappings...")

    # Update imports
    total_files_changed = 0
    total_changes = 0
    detailed_changes = {}

    for file_path in python_files:
        num_changes, changes = update_imports_in_file(file_path, IMPORT_MAPPINGS)
        if num_changes > 0:
            total_files_changed += 1
            total_changes += num_changes
            relative_path = file_path.relative_to(backend_dir)
            detailed_changes[str(relative_path)] = changes

    # Print results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"\n✅ Files updated: {total_files_changed}")
    print(f"✅ Total import changes: {total_changes}")

    if detailed_changes:
        print("\n📋 Detailed Changes:\n")
        for file_path, changes in sorted(detailed_changes.items()):
            print(f"📄 {file_path}")
            for change in changes:
                print(change)
            print()

    # Delete bridge modules
    print("\n" + "=" * 80)
    print("DELETING BRIDGE MODULES")
    print("=" * 80)
    deleted = delete_bridge_modules(api_dir, BRIDGE_MODULES)
    print(f"\n✅ Deleted {deleted} of {len(BRIDGE_MODULES)} bridge modules")

    # Final verification
    print("\n" + "=" * 80)
    print("FINAL VERIFICATION")
    print("=" * 80)

    remaining_root_files = [f for f in api_dir.glob("*.py") if f.name != "__init__.py"]
    print(f"\n📊 Remaining root .py files in app/api/: {len(remaining_root_files)}")
    if remaining_root_files:
        print("   Files:")
        for f in remaining_root_files:
            print(f"   - {f.name}")

    print("\n✅ Phase 6: Import Update COMPLETE")
    print("\nNext: Phase 7 - Backend Testing")

    return 0

if __name__ == "__main__":
    exit(main())
