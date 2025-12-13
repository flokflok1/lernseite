# LernsystemX Database Migrations

## Overview

This directory contains 40 SQL migration files that define the complete LernsystemX database schema.

**Total Migrations:** 40
**Total Tables:** 102+
**Database:** PostgreSQL 14+

## Migration Structure

Migrations are numbered from `001` to `040` and must be executed in sequential order to maintain referential integrity.

### Migration Groups

#### Core System (001-007)
- **001_core_users_roles.sql** - Users, roles, permissions, sessions, recovery codes
- **002_security_auth.sql** - Login attempts, 2FA, password reset, email verification, security audit
- **003_organisations.sql** - Organizations, members, classes, enrollments
- **004_organisation_settings.sql** - Organization settings, branding, features, quotas
- **005_api_gateway.sql** - API clients, keys, routes, request logs, webhooks
- **006_audit_logging.sql** - Audit logs, data access logs, change history
- **007_system_settings.sql** - System settings, feature flags, maintenance windows

#### Course & Learning (008-016)
- **008_courses.sql** - Courses, categories, access, reviews
- **009_chapters.sql** - Chapters, theory, resources
- **010_lessons.sql** - Lessons, completions
- **011_learning_methods.sql** - 32 learning methods (LM00-LM31), completions
- **012_learning_progress.sql** - Enrollments, progress, streaks, achievements
- **013_exams.sql** - Exams, questions
- **014_exam_results.sql** - Attempts, results, answers
- **015_certificates.sql** - Certificate templates, issued certificates
- **016_certificates_progress.sql** - Requirements, skills, endorsements

#### AI System (017-021)
- **017_ai_providers.sql** - AI providers (OpenAI, Anthropic, etc.), health monitoring
- **018_ai_models.sql** - AI models with pricing and capabilities
- **019_ai_prompts.sql** - Prompt templates, versions, method mappings
- **020_ai_usage_logs.sql** - KI requests, raw inputs, usage aggregates
- **021_ai_jobs.sql** - Async AI job queue, job steps

#### Analytics & Gamification (022-025)
- **022_analytics_core.sql** - Analytics sessions, aggregates
- **023_analytics_events.sql** - Detailed event tracking
- **024_gamification.sql** - XP system, transactions, leaderboards
- **025_badges.sql** - Badges, user badges

#### LiveRooms (026-027)
- **026_liverooms_core.sql** - Rooms, participants
- **027_liverooms_chat.sql** - Whiteboards, transcripts, recordings, logs, AI stats

#### Notifications (028-030)
- **028_notifications_core.sql** - Notifications, preferences
- **029_notifications_templates.sql** - Templates, channels
- **030_notifications_logs.sql** - Delivery logs, email queue

#### Media & Storage (031-032)
- **031_media_files.sql** - Media files, thumbnails
- **032_storage_versions.sql** - File versions, content versions

#### Billing & Payments (033-035)
- **033_billing_core.sql** - Subscriptions, payment methods
- **034_billing_subscriptions.sql** - Subscription plans, changes
- **035_billing_transactions.sql** - Token wallets, transactions, payment history

#### Community (036-037)
- **036_community_core.sql** - Groups, members, resources
- **037_community_messages.sql** - Messages, discussions, posts

#### System Infrastructure (038-040)
- **038_translations.sql** - Translations (20 languages), cache, supported languages
- **039_rate_limits.sql** - Rate limits, hits, quota usage
- **040_integrity_checks.sql** - RLS policies, constraints, functions, views, verification

## Running Migrations

### Automatic (via Setup Wizard)

```bash
python run.py
# Navigate to http://localhost:5000/setup/status
# Click "Initialize Database"
```

### Manual (via Migration Manager)

```python
from backend.setup.migrations import MigrationManager

# List all migrations
migrations = MigrationManager.list_migrations()

# Run all pending migrations
result = MigrationManager.run_pending_migrations()
```

### Direct SQL Execution

```bash
# Execute migrations in order
for i in {001..040}; do
    psql -U postgres -d lernsystemx_dev -f $(printf "%03d" $i)_*.sql
done
```

## Migration Naming Convention

```
{number}_{descriptive_name}.sql

Examples:
001_core_users_roles.sql
020_ai_usage_logs.sql
040_integrity_checks.sql
```

## Important Notes

### Prerequisites
- PostgreSQL 14+ with `uuid-ossp` and `pgcrypto` extensions
- Migrations must be run in sequential order (001 → 040)
- Each migration is idempotent (can be re-run safely)

### System Seeds
The following migrations include system seed data:
- **001** - Standard roles (free, premium, creator, etc.)
- **007** - System settings
- **017** - AI providers (OpenAI, Anthropic, Google)
- **018** - AI models (GPT-4o, Claude, etc.)
- **034** - Subscription plans
- **038** - Supported languages (20 languages)

### No Demo Data
These migrations contain **structure only** + **system seeds**. No demo courses, users, or content.

## Table Count by Migration

| Migration | Tables Created |
|-----------|---------------|
| 001 | 6 (users, roles, permissions, role_permissions, user_sessions, recovery_codes) |
| 002 | 6 (login_attempts, 2fa_backups, password_reset, email_verification, security_audit, blocked_ips) |
| 003 | 4 (organizations, members, classes, enrollments) |
| 004 | 4 (org_settings, branding, features, quotas) |
| 005 | 5 (api_clients, keys, routes, logs, webhooks) |
| 006 | 3 (audit_logs, data_access_logs, change_history) |
| 007 | 3 (system_settings, feature_flags, maintenance_windows) |
| 008 | 4 (courses, categories, access, reviews) |
| 009 | 3 (chapters, theory, resources) |
| 010 | 2 (lessons, completions) |
| 011 | 2 (learning_methods, completions) |
| 012 | 4 (enrollments, progress, streaks, achievements) |
| 013 | 2 (exams, questions) |
| 014 | 3 (attempts, results, answers) |
| 015 | 2 (templates, certificates) |
| 016 | 3 (requirements, skills, endorsements) |
| 017 | 2 (providers, health) |
| 018 | 1 (models) |
| 019 | 3 (prompts, versions, mappings) |
| 020 | 3 (ki_requests, raw_inputs, aggregates) |
| 021 | 2 (jobs, steps) |
| 022 | 2 (sessions, aggregates) |
| 023 | 1 (events) |
| 024 | 3 (xp, transactions, leaderboards) |
| 025 | 2 (badges, user_badges) |
| 026 | 2 (rooms, participants) |
| 027 | 5 (whiteboards, transcripts, recordings, logs, ai_stats) |
| 028 | 2 (notifications, preferences) |
| 029 | 2 (templates, channels) |
| 030 | 2 (logs, email_queue) |
| 031 | 2 (files, thumbnails) |
| 032 | 2 (file_versions, content_versions) |
| 033 | 2 (subscriptions, payment_methods) |
| 034 | 2 (plans, changes) |
| 035 | 3 (wallets, transactions, history) |
| 036 | 3 (groups, members, resources) |
| 037 | 3 (messages, discussions, posts) |
| 038 | 3 (translations, cache, languages) |
| 039 | 3 (limits, hits, quota_usage) |
| 040 | 0 (RLS policies, functions, views) |

**Total: 102 tables**

## Verification

After running all migrations, verify installation:

```sql
-- Count tables
SELECT COUNT(*) FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
-- Expected: 102

-- Check for migration history
SELECT * FROM migration_history ORDER BY executed_at DESC;

-- Verify RLS is enabled
SELECT tablename, rowsecurity FROM pg_tables
WHERE schemaname = 'public' AND rowsecurity = true;
```

## Rollback

Migrations do NOT include down/rollback scripts. For rollback:
- Restore from database backup
- Or manually drop schema: `DROP SCHEMA public CASCADE; CREATE SCHEMA public;`

## Support

For migration issues, check:
1. `migration_history` table for execution status
2. PostgreSQL logs for SQL errors
3. Setup Wizard diagnostics at `/setup/status`

---

**Generated:** 2025-01-17
**Version:** 1.0.0
**Database:** PostgreSQL 14+
