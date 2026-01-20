# Migration History Archive

**Status:** Historical Reference Only
**Date Created:** 2026-01-18
**Purpose:** Documentation of deprecated/refactored migrations

---

## Overview

This directory contains **historical migration files** that have been refactored, consolidated, or replaced by newer migrations. These files are **NOT** applied to the database and are kept for reference only.

All currently active migrations are in `backend/migrations/` organized by feature areas.

---

## Archive Contents

### Consolidated Migrations

These migrations were split/consolidated into multiple files in the active migrations directory:

| Old File | Reason | New Location |
|----------|--------|--------------|
| `048_ai_authoring_studio.sql` | Split into 3 parts (size >500 lines) | `migrations/03_AI/048_ai_authoring_studio_part1/2/3.sql` |
| `053_capability_slots.sql` | Split into 2 parts | `migrations/03_AI/053_capability_slots_part1/2.sql` |
| `094_agent_global_knowledge.sql` | Split into 2 parts | `migrations/03_AI/094_agent_global_knowledge_part1/2.sql` |

### Refactored Migrations

These migrations were refactored with different approaches in the active directory:

| Old File | Changes | Status |
|----------|---------|--------|
| `038_i18n_complete.sql` | Refactored as modular i18n system | Active in `11_System/i18n/` (084-088) |
| `064_math_toolkit.sql` | Integrated into capability slots | Consolidated |
| `072_i18n_system.sql` | Consolidated into modular i18n | Active in `11_System/i18n/` (084-088) |
| `076_multi_tenancy_extensions.sql` | Refactored architecture | Under review |
| `076_feature_flags.sql` | Reorganized feature flag system | Consolidated |
| `077_consolidate_i18n_migrations.sql` | Consolidated into modular i18n | Active in `11_System/i18n/` (084-088) |
| `077_i18n_sync_system.sql` | Refactored in modular approach | Active in `11_System/i18n/` (086) |
| `078_language_progress_triggers.sql` | Triggers refactored | Active in `11_System/i18n/` (087) |
| `078_row_level_security.sql` | RLS policies updated | Consolidated |
| `079_update_i18n_namespaces.sql` | Refactored namespaces | Active in `11_System/i18n/` (088) |
| `070_i18n_sync_system.sql` | Refactored in modular approach | Active in `11_System/i18n/` (086) |

### Superseded Migrations

These migrations were replaced or integrated into newer migrations:

| Old File | Replaced By | Reason |
|----------|-------------|--------|
| `067_add_owner_admin.sql` | Multiple migrations | Permissions refactored |
| `067_ai_model_profiles_base.sql` | `92_ai_model_profiles_base.sql` | Renumbered for clarity |
| `068_course_ai_settings.sql` | `93_course_ai_settings.sql` | Renumbered for clarity |
| `068_role_feature_assignments.sql` | Integrated into core | Consolidated |
| `069_agent_global_knowledge.sql` | `094_agent_global_knowledge_*.sql` | Split + renumbered |
| `069_permission_thresholds.sql` | Integrated into core | Consolidated |
| `079_social_posts.sql` | `96_social_posts.sql` | Moved to Social folder |
| `080_social_follows.sql` | `97_social_follows.sql` | Moved to Social folder |
| `081_social_engagement.sql` | `98_social_engagement.sql` | Moved to Social folder |

---

## Why Archive in Separate Directory?

### Professional Standards

1. **Clean Migration Directory**
   - Active migrations only (no clutter)
   - Clear execution path
   - Easy auditing

2. **Safety**
   - Prevents accidental re-application of old migrations
   - Clear separation: "active" vs "historical"

3. **Compliance**
   - Git history captures the original intent
   - Archive directory documents the refactoring rationale
   - Traceable decision trail

### Best Practice Structure

```
backend/
├── migrations/              ← ACTIVE ONLY (applied to DB)
│   ├── 00_Seeds/
│   ├── 01_Core/
│   ├── 02_Content/
│   ├── 03_AI/
│   ├── 04_Analytics/
│   ├── ... (etc)
│   ├── 11_System/
│   │   ├── 039_rate_limits.sql
│   │   ├── 040_integrity_checks.sql
│   │   ├── i18n/            ← ACTIVE i18n migrations (084-088)
│   │   │   ├── 084_i18n_core_tables.sql
│   │   │   ├── 085_i18n_languages_base.sql
│   │   │   ├── 086_i18n_sync_system.sql
│   │   │   ├── 087_i18n_progress_triggers.sql
│   │   │   └── 088_i18n_namespaces.sql
│   │   └── ... (etc)
│   └── MIGRATION_GAPS.md    (documents intentional gaps)
│
└── .migration-history/      ← ARCHIVE (reference only)
    ├── README.md            (this file)
    ├── *.sql                (deprecated/refactored files from root archive)
    └── 11_System_Archives/  (nested i18n archives)
        ├── 2026-01-13/      (old i18n consolidation attempt)
        │   ├── 038_translations.sql
        │   ├── 072_i18n_system.sql
        │   └── 077_consolidate_i18n_migrations.sql
        └── 2026-01-16/      (second i18n migration attempt)
            ├── 077_i18n_sync_system.sql
            ├── 078_language_progress_triggers.sql
            └── 079_update_i18n_namespaces.sql
```

---

## Complete Archive Inventory

### Root Archive (18 files from backend/migrations/.archive_2026-01-16/)
Located in: `.migration-history/`

**AI Authoring & Capabilities:**
- `048_ai_authoring_studio_part1.sql`
- `048_ai_authoring_studio_part2.sql`
- `048_ai_authoring_studio_part3.sql`
- `053_capability_slots_part1.sql`
- `053_capability_slots_part2.sql`
- `094_agent_global_knowledge_part1.sql`
- `094_agent_global_knowledge_part2.sql`

**Permissions & Features:**
- `067_add_owner_admin.sql`
- `067_ai_model_profiles_base.sql`
- `068_course_ai_settings.sql`
- `068_role_feature_assignments.sql`
- `069_permission_thresholds.sql`

**Social Network:**
- `079_social_posts.sql`
- `080_social_follows.sql`
- `081_social_engagement.sql`

**System & Security:**
- `076_multi_tenancy_extensions.sql`
- `076_feature_flags.sql`
- `078_row_level_security.sql`

### i18n Archives (6 files from backend/migrations/11_System/.archive_*)
Located in: `.migration-history/11_System_Archives/`

**From 2026-01-13 (old consolidation attempt):**
- `038_translations.sql` - Original translation tables
- `072_i18n_system.sql` - Early i18n system version
- `077_consolidate_i18n_migrations.sql` - First consolidation attempt

**From 2026-01-16 (second attempt):**
- `077_i18n_sync_system.sql` - i18n sync implementation (v2)
- `078_language_progress_triggers.sql` - Progress tracking triggers
- `079_update_i18n_namespaces.sql` - Namespace updates

**Currently Active (migrations/11_System/i18n/):**
- `084_i18n_core_tables.sql` - Final core i18n tables ✅
- `085_i18n_languages_base.sql` - Language definitions ✅
- `086_i18n_sync_system.sql` - Final sync system ✅
- `087_i18n_progress_triggers.sql` - Final progress triggers ✅
- `088_i18n_namespaces.sql` - Final namespace system ✅

**Total Archive Inventory:** 24 files

---

## Reference: Database Current State

### Phase 0 Database (17 tables - All Active Migrations)

**ai_pipeline schema (15 tables):**
- ai_editor_refinement_history (068)
- ai_editor_session_history (067)
- ai_editor_sessions (067)
- change_records (072)
- collaboration_comments (072)
- content_block_collaborators (072)
- generated_theory_sheets (060)
- interactive_scenarios (071)
- learning_path_steps (070)
- learning_paths (070)
- material_resources (073)
- material_usage (073)
- prompt_template_usage (060)
- prompt_templates (060)
- scenario_interactions (071)

**analytics schema (2 tables):**
- ai_editor_analytics (074)
- ai_editor_insights (074)

✅ **All from active migrations only**
❌ **No tables from archive files**

---

## How to Use This Archive

### For Research/Understanding
If you need to understand why a migration was refactored, refer to the corresponding file here.

### For Git History
```bash
# See the history of a refactored migration
git log --follow backend/.migration-history/048_ai_authoring_studio.sql

# See when it was consolidated
git log --follow backend/migrations/03_AI/048_ai_authoring_studio_part1.sql
```

### NEVER Apply These Files
❌ Do NOT manually apply any file from this directory
❌ Do NOT import schema from these files
❌ They may contain outdated constraints or references

---

## Maintenance Guidelines

### When Adding New Migrations
1. ✅ Add to `backend/migrations/XX_Feature/` (active)
2. ✅ Keep under 500 lines per file
3. ❌ Do NOT add to `.migration-history/` (archive only)

### When Refactoring Existing Migrations
1. ✅ Create new versioned file in active directory
2. ✅ Move old file here with explanation
3. ✅ Update this README with rationale
4. ✅ Ensure new migration is idempotent (`IF NOT EXISTS`)

### When Discovering Old Migrations in Database
If you find tables that match archived migrations:
```sql
-- Check if table exists and where it came from
SELECT table_schema, table_name, table_type
FROM information_schema.tables
WHERE table_name LIKE '%old_pattern%';
```

If found in production:
1. Document the migration number it came from
2. Add note to this README
3. Plan removal/consolidation

---

## Related Documentation

- `backend/migrations/MIGRATION_GAPS.md` - Documents intentional gaps in active migration numbers
- `backend/migrations/` - Currently active migrations
- `.claude/PHASE0_COMPLETION_FINAL_2026-01-18.md` - Phase 0 completion details
- `.claude/MIGRATION_CONSOLIDATION_COMPLETE.md` - Past consolidation history

---

## Professional Migration Standards

### Active Migration Directory Rules
- ✅ Sequentially numbered (no gaps documented in MIGRATION_GAPS.md)
- ✅ Organized by feature folder
- ✅ Each file < 500 lines (split if needed)
- ✅ Clear naming (descriptive, not `_old` or `_backup`)
- ✅ Header comment identifies migration purpose
- ✅ Idempotent (`IF NOT EXISTS` / `IF NOT NULL`)

### Archive Directory Rules
- ✅ Separate from active migrations
- ✅ Documented with rationale
- ✅ Never applied to database
- ✅ Preserved for historical reference
- ✅ Linked to Git history

---

**Archive Created:** 2026-01-18
**Last Updated:** 2026-01-18 (Complete cleanup + nested archives documented)
**Maintained By:** Senior Dev (Claude Code)
**Status:** Professional Structure Compliant ✅
**Setup Wizard Verification:** ✅ PASSES - Will load 106 active migrations, 0 archived migrations

