#!/usr/bin/env python3
"""
Complete i18n restructure - consolidate AI Editor & split large files
"""
import json
from pathlib import Path
from collections import OrderedDict
import shutil

LOCALES_DIR = Path('.')
LANGUAGES = ['de', 'en', 'pl']


def sort_json_keys(obj):
    """Recursively sort JSON keys alphabetically."""
    if isinstance(obj, dict):
        return OrderedDict(sorted((k, sort_json_keys(v)) for k, v in obj.items()))
    elif isinstance(obj, list):
        return [sort_json_keys(item) for item in obj]
    else:
        return obj


def save_json(path: Path, data: dict):
    """Save JSON file with proper formatting."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(sort_json_keys(data), f, ensure_ascii=False, indent=2)


def restructure_language(lang: str):
    """Restructure for one language."""
    print(f"\n{'='*60}")
    print(f"Processing {lang.upper()}...")
    print('='*60)

    lang_dir = LOCALES_DIR / lang

    # =================================================================
    # 1. Consolidate AI Editor from admin/ai.json + features/aiEditor.json
    # =================================================================
    print("\n📦 Consolidating AI Editor...")

    # Load admin/ai.json (has aiEditor key)
    admin_ai_file = lang_dir / 'admin' / 'ai.json'
    with open(admin_ai_file, 'r', encoding='utf-8') as f:
        admin_ai_data = json.load(f)

    ai_editor_from_admin = admin_ai_data.pop('aiEditor', {})

    # Load features/aiEditor.json
    features_ai_editor_file = lang_dir / 'features' / 'aiEditor.json'
    with open(features_ai_editor_file, 'r', encoding='utf-8') as f:
        features_ai_editor_data = json.load(f)

    # Create aiEditor directory
    ai_editor_dir = lang_dir / 'aiEditor'
    ai_editor_dir.mkdir(exist_ok=True)

    # Split features/aiEditor.json into logical submodules
    ai_editor_splits = {
        'admin.json': ai_editor_from_admin,  # Admin-specific settings
        'features.json': {
            k: v for k, v in features_ai_editor_data.items()
            if k in ['aiEditorFeatures', 'aiEditorNav', 'aiEditorInfo']
        },
        'chat.json': {
            k: v for k, v in features_ai_editor_data.items()
            if k in ['aiEditorChat', 'aiEditorChatBubble', 'aiEditorChatHistory']
        },
        'content.json': {
            k: v for k, v in features_ai_editor_data.items()
            if k in ['aiEditorContent', 'aiEditorContentEditor', 'aiEditorContentPreview']
        },
        'generation.json': {
            k: v for k, v in features_ai_editor_data.items()
            if k in ['aiEditorGeneration', 'aiEditorGenerationProgress']
        },
        'materials.json': {
            k: v for k, v in features_ai_editor_data.items()
            if k in ['aiEditorMaterials', 'aiEditorMaterialsList']
        },
        'panels.json': {
            k: v for k, v in features_ai_editor_data.items()
            if 'Panel' in k or 'Tab' in k
        },
        'settings.json': {
            k: v for k, v in features_ai_editor_data.items()
            if 'Settings' in k or 'Config' in k
        },
        'toolbar.json': {
            k: v for k, v in features_ai_editor_data.items()
            if 'Toolbar' in k or 'Button' in k
        }
    }

    # Add remaining keys to common.json
    all_split_keys = set()
    for split_data in ai_editor_splits.values():
        all_split_keys.update(split_data.keys())

    remaining_keys = set(features_ai_editor_data.keys()) - all_split_keys
    if remaining_keys:
        ai_editor_splits['common.json'] = {
            k: features_ai_editor_data[k] for k in remaining_keys
        }

    # Save AI Editor submodules
    for filename, data in ai_editor_splits.items():
        if data:  # Only save if has content
            save_json(ai_editor_dir / filename, data)
            print(f"  ✓ Created aiEditor/{filename} ({len(data)} keys)")

    # Create index.ts for aiEditor
    index_files = [f.stem for f in ai_editor_dir.glob('*.json')]
    index_imports = '\n'.join([f"import {name} from './{name}.json'" for name in index_files])
    index_exports = '\n  ' + ',\n  '.join([f'...{name}' for name in index_files])

    index_content = f"""// Auto-generated barrel export for AI Editor submodules
{index_imports}

export default {{{index_exports}
}}
"""

    with open(ai_editor_dir / 'index.ts', 'w', encoding='utf-8') as f:
        f.write(index_content)
    print(f"  ✓ Created aiEditor/index.ts")

    # Update admin/ai.json (remove aiEditor key)
    save_json(admin_ai_file, admin_ai_data)
    print(f"  ✓ Updated admin/ai.json (removed aiEditor)")

    # Remove old features/aiEditor.json
    features_ai_editor_file.unlink()
    print(f"  ✓ Removed features/aiEditor.json")

    # =================================================================
    # 2. Split courses.json
    # =================================================================
    print("\n📦 Splitting courses...")

    courses_file = lang_dir / 'courses.json'
    with open(courses_file, 'r', encoding='utf-8') as f:
        courses_data = json.load(f)

    courses_dir = lang_dir / 'courses'
    courses_dir.mkdir(exist_ok=True)

    courses_splits = {
        'courses.json': {
            k: v for k, v in courses_data.items()
            if k in ['courses', 'courseEditor', 'creator', 'publishing']
        },
        'content.json': {
            k: v for k, v in courses_data.items()
            if k in ['chapter', 'chapterTheory', 'lesson', 'examSimulation']
        },
        'moderation.json': {
            k: v for k, v in courses_data.items()
            if k in ['moderation']
        }
    }

    for filename, data in courses_splits.items():
        save_json(courses_dir / filename, data)
        print(f"  ✓ Created courses/{filename} ({len(data)} keys)")

    # Create index.ts for courses
    index_content = """// Auto-generated barrel export for courses submodules
import courses from './courses.json'
import content from './content.json'
import moderation from './moderation.json'

export default {
  ...courses,
  ...content,
  ...moderation
}
"""

    with open(courses_dir / 'index.ts', 'w', encoding='utf-8') as f:
        f.write(index_content)
    print(f"  ✓ Created courses/index.ts")

    # Remove old courses.json
    courses_file.unlink()
    print(f"  ✓ Removed courses.json")


def update_i18n_plugin():
    """Update i18n.ts to import from new structure."""
    print("\n🔧 Updating i18n.ts...")

    i18n_file = Path('..') / 'plugins' / 'i18n.ts'

    # Read current content
    with open(i18n_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update imports
    replacements = {
        # Courses
        "import deCourses from '@/locales/de/courses.json'": "import deCourses from '@/locales/de/courses/index'",
        "import enCourses from '@/locales/en/courses.json'": "import enCourses from '@/locales/en/courses/index'",
        "import plCourses from '@/locales/pl/courses.json'": "import plCourses from '@/locales/pl/courses/index'",

        # AI Editor (remove old features/aiEditor)
        "import deFeaturesAiEditor from '@/locales/de/features/aiEditor.json'": "",
        "import enFeaturesAiEditor from '@/locales/en/features/aiEditor.json'": "",
        "import plFeaturesAiEditor from '@/locales/pl/features/aiEditor.json'": "",
    }

    for old, new in replacements.items():
        content = content.replace(old, new)

    # Add AI Editor imports after admin imports
    ai_editor_imports = """import deAiEditor from '@/locales/de/aiEditor/index'
import enAiEditor from '@/locales/en/aiEditor/index'
import plAiEditor from '@/locales/pl/aiEditor/index'
"""

    # Find position after admin imports
    admin_import_line = "import deAdmin from '@/locales/de/admin/index'"
    insertion_pos = content.find(admin_import_line)
    if insertion_pos != -1:
        # Find end of line
        line_end = content.find('\n', insertion_pos)
        content = content[:line_end + 1] + ai_editor_imports + content[line_end + 1:]

    # Update feature modules merging (remove aiEditor references)
    content = content.replace('...deFeaturesAiEditor,', '')
    content = content.replace('...enFeaturesAiEditor,', '')
    content = content.replace('...plFeaturesAiEditor,', '')

    # Update merge statements to include aiEditor
    content = content.replace(
        'const de = { ...deCommon, ...deAdmin, ...deFeatures',
        'const de = { ...deCommon, ...deAdmin, ...deAiEditor, ...deFeatures'
    )
    content = content.replace(
        'const en = { ...enCommon, ...enAdmin, ...enFeatures',
        'const en = { ...enCommon, ...enAdmin, ...enAiEditor, ...enFeatures'
    )
    content = content.replace(
        'const pl = { ...plCommon, ...plAdmin, ...plFeatures',
        'const pl = { ...plCommon, ...plAdmin, ...plAiEditor, ...plFeatures'
    )

    # Write updated content
    with open(i18n_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print("  ✓ Updated i18n.ts with new imports")


def main():
    print("🔧 Complete i18n restructure starting...")
    print("="*60)
    print("Strategy:")
    print("  1. Consolidate ALL AI Editor content → aiEditor/")
    print("  2. Split courses.json → courses/")
    print("  3. Update i18n.ts imports")
    print("="*60)

    for lang in LANGUAGES:
        restructure_language(lang)

    update_i18n_plugin()

    print("\n" + "="*60)
    print("✅ Restructure complete!")
    print("="*60)
    print("\nNew structure:")
    print("  aiEditor/     - ALL AI Editor content (no duplicates!)")
    print("  admin/        - Admin features (without aiEditor)")
    print("  courses/      - Course content")
    print("  features/     - Other features")


if __name__ == '__main__':
    main()
