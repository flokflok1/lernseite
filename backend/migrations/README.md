# Database Migrations

> **105 Migrations** in **13 Kategorien** - PostgreSQL Schema für LernsystemX

---

## Ordnerstruktur

| Ordner | Anzahl | Beschreibung |
|--------|--------|--------------|
| [00_Seeds](#00_seeds) | 1 | Seed-Daten (AP1 FISI Kurs) |
| [01_Core](#01_core) | 23 | Users, Roles, Security, Organisations, Groups, Permissions |
| [02_Content](#02_content) | 19 | Courses, Chapters, Lessons, LMs, Exams, Categories |
| [03_AI](#03_ai) | 26 | Providers, Models, Prompts, Agents, TTS, Authoring |
| [04_Analytics](#04_analytics) | 3 | Analytics, Events, Feedback |
| [05_Gamification](#05_gamification) | 2 | XP, Badges |
| [06_LiveRoom](#06_liveroom) | 2 | Rooms, Chat |
| [07_Notifications](#07_notifications) | 3 | Notifications, Templates |
| [08_Storage](#08_storage) | 3 | Media Files, Cache |
| [09_Billing](#09_billing) | 3 | Subscriptions, Transactions |
| [10_Community](#10_community) | 2 | Groups, Messages |
| [11_System](#11_system) | 13 | i18n, Rate Limits, Features, Feature Flags, Dashboard |
| [12_Social](#12_social) | 5 | Content Moderation, Child Safety, Social Network |

---

## Schema-Regeln (WICHTIG)

**ALLE Tabellen MÜSSEN in benannten Schemas erstellt werden!**

```sql
-- ✅ KORREKT
CREATE TABLE IF NOT EXISTS core.users (...);
CREATE TABLE IF NOT EXISTS courses.courses (...);

-- ❌ VERBOTEN
CREATE TABLE IF NOT EXISTS users (...);  -- public schema!
```

**Erlaubte Schemas:**
- `core` - Users, Roles, Auth, Settings
- `courses` - Kurse, Kapitel, Lektionen
- `learning_methods` - LM-Typen, Instanzen
- `organisations` - Organisationen, Members
- `analytics` - Analytics, Events
- `gamification` - XP, Badges
- `liveroom` - LiveRoom, Chat
- `notifications` - Notifications
- `media` - Medien/Dateien
- `billing` - Abrechnung, Subscriptions
- `community` - Community, Groups
- `support_systems` - System Features, Feature Flags
- `i18n` - Internationalization
- `social` - Social Network (Posts, Follows, etc.)
- `moderation` - Content Moderation
- `compliance` - GDPR, COPPA, DSA Compliance

---

## 00_Seeds

Seed-Daten für Test und Entwicklung.

| Datei | Beschreibung |
|-------|--------------|
| seed_ap1_fisi_course.sql | AP1 FISI Beispiel-Kurs |

---

## 01_Core

Users, Authentifizierung, Organisationen, Berechtigungen.

| Nr | Datei | Beschreibung |
|----|-------|--------------|
| 000 | schemas | **Zentrale Schema-Erstellung** |
| 000 | functions | Globale SQL-Funktionen |
| 001 | users_table | core.users |
| 002 | security_auth | Sessions, Tokens, 2FA |
| 003 | organisations | organisations.organisations, members |
| 004 | organisation_settings | org_settings, branding |
| 005 | api_gateway | api_keys, routes, logs |
| 006 | audit_logging | audit_logs, data_access |
| 007 | system_settings | settings, flags, maintenance |
| 008 | user_preferences | user_preferences JSONB |
| 009 | config_system | system_config, lookup_types |
| 010 | multi_tenancy_extensions_part1 | Branding, Feature Flags |
| 011 | multi_tenancy_extensions_part2 | Org Audit |
| 013 | row_level_security_part1 | RLS Policies |
| 014 | row_level_security_part2 | RLS Policies (continued) |
| 020 | groups_table | core.groups (RBAC) |
| 021 | users_groups_junction | core.users_groups |
| 022 | permissions_registry | core.permissions |
| 023 | group_permissions_mapping | core.group_permissions |
| 024 | modify_users_for_groups | User-Group Extensions |
| 025 | b2b_contact_requests | B2B Contact Forms |
| 026 | add_frontend_role_to_groups | Frontend Roles |
| 027 | add_hierarchy_level_to_groups | Group Hierarchy |

---

## 02_Content

Kurse, Kapitel, Lektionen, Lernmethoden, Prüfungen.

| Nr | Datei | Beschreibung |
|----|-------|--------------|
| 008 | courses | courses.courses, enrollments |
| 009 | chapters | courses.chapters |
| 010 | lessons | courses.lessons, content |
| 011 | learning_methods | learning_methods.learning_method_types |
| 012 | learning_progress | progress, completions |
| 013 | exams | exams, questions |
| 014 | exam_results | attempts, scores |
| 015 | certificates | certificates, templates |
| 016 | certificates_progress | cert_progress |
| 043 | course_prompts | Kurs-Prompt Overrides |
| 044 | course_files | Datei-Anhänge |
| 046 | rename_modules_to_chapters | Module→Chapter Refactoring |
| 047 | learning_methods_module_to_chapter | LM Module→Chapter |
| 049 | flexible_categories | Hierarchische Kategorien |
| 062 | lm_19_content_methods | Content-LMs (aktuell 12) |
| 064 | consolidated | Math Toolkit, Consolidated |
| 065 | exam_simulation_tables | Prüfungssimulation |
| 067 | lm_plugins | LM Plugins System |
| 078 | add_ui_schema | UI Schema |

---

## 03_AI

KI-Provider, Modelle, Prompts, Agents, TTS, Authoring.

| Nr | Datei | Beschreibung |
|----|-------|--------------|
| 017 | ai_providers | providers, config |
| 018 | ai_models | models, capabilities |
| 019 | ai_prompts | templates, versions |
| 020 | ai_usage_logs | requests, token_usage |
| 021 | ai_jobs | jobs, queue, results |
| 045 | ai_models | Extended Model Registry |
| 048 | consolidated | Authoring Studio |
| 050 | ai_models_sync_support | API Sync für Models |
| 052 | learning_method_model_routing | LM Model Routing |
| 053 | consolidated | Capability Slots |
| 055 | smart_agent_system | Smart Agent System |
| 058 | learning_method_ai_tables | LM AI Tables |
| 059 | tts_pronunciation | TTS Aussprache |
| 060 | prompt_templates | Prompt Template System |
| 061 | authoring_actions | Authoring Actions |
| 066 | course_authoring_sessions | Authoring Sessions |
| 067 | ai_editor_sessions | AI Editor Sessions |
| 068 | ai_editor_refinement | AI Editor Refinement |
| 070 | learning_paths | Learning Paths |
| 071 | interactive_scenarios | Interactive Scenarios |
| 072 | collaboration | Collaboration Tools |
| 073 | analytics | AI Analytics |
| 074 | material_recommendations | Material Recommendations |
| 092 | ai_model_profiles_base | AI Model Profiles |
| 093 | course_ai_settings | Course AI Settings |
| 094 | consolidated | AI Consolidated |

---

## 04_Analytics

Analytics, Events, Feedback.

| Nr | Datei | Beschreibung |
|----|-------|--------------|
| 022 | analytics_core | analytics.analytics_sessions, aggregates |
| 023 | analytics_events | analytics.analytics_events |
| 057 | feedback_system | support_systems.user_feedback |

---

## 05_Gamification

| Nr | Datei | Beschreibung |
|----|-------|--------------|
| 024 | gamification | gamification.xp, levels, streaks |
| 025 | badges | gamification.badges, user_badges |

---

## 06_LiveRoom

| Nr | Datei | Beschreibung |
|----|-------|--------------|
| 026 | liverooms_core | liveroom.rooms, participants |
| 027 | liverooms_chat | liveroom.messages, whiteboards |

---

## 07_Notifications

| Nr | Datei | Beschreibung |
|----|-------|--------------|
| 028 | notifications_core | notifications.notifications |
| 029 | notifications_templates | notifications.templates |
| 030 | notifications_logs | notifications.delivery_logs |

---

## 08_Storage

| Nr | Datei | Beschreibung |
|----|-------|--------------|
| 031 | media_files | media.files, metadata |
| 032 | storage_versions | media.versions, cleanup |
| 056 | agent_media_cache | media.agent_media_cache |

---

## 09_Billing

| Nr | Datei | Beschreibung |
|----|-------|--------------|
| 033 | billing_core | billing.plans, pricing |
| 034 | billing_subscriptions | billing.subscriptions, tokens |
| 035 | billing_transactions | billing.transactions, invoices |

---

## 10_Community

| Nr | Datei | Beschreibung |
|----|-------|--------------|
| 036 | community_core | community.groups, memberships |
| 037 | community_messages | community.posts, comments |

---

## 11_System

System-Tabellen, i18n, Feature Flags.

| Nr | Datei | Beschreibung |
|----|-------|--------------|
| 039 | rate_limits | core.rate_limits, quotas |
| 040 | integrity_checks | Constraints, triggers |
| 041 | feature_based_authorization | Feature-based Auth |
| 074 | system_features | support_systems.system_features |
| 075 | dashboard_widget_system | Dashboard Widgets |
| 095 | feature_flags_core | support_systems.feature_flags (Dark Launch) |
| 096 | feature_flags_enterprise | Role/Tier mappings, Rollout Plans |
| 097 | feature_flags_advanced | Cache, Audit, Snapshots |

### i18n Subfolder

| Nr | Datei | Beschreibung |
|----|-------|--------------|
| 084 | i18n_core_tables | i18n.translations |
| 085 | i18n_languages_base | i18n.languages |
| 086 | i18n_sync_system | Sync System |
| 087 | i18n_progress_triggers | Progress Triggers |
| 088 | i18n_namespaces | i18n.namespaces |

---

## 12_Social (NEU)

Social Network, Content Moderation, DSA/NetzDG Compliance.

| Nr | Datei | Beschreibung |
|----|-------|--------------|
| 082 | content_moderation | moderation.content_reports, actions, queue |
| 083 | child_safety | compliance.age_verifications, parental_controls |
| 096 | social_posts | social.social_posts, media, hashtags |
| 097 | social_follows | social.social_follows, user_stats |
| 098 | social_engagement | social.social_likes, comments, shares |

---

## Migration-Ausführung

```bash
# Migrations ausführen (Reihenfolge wichtig!)
# 1. 01_Core/000_schemas.sql (IMMER ZUERST!)
# 2. 01_Core - Core Tabellen
# 3. 02_Content - Content Tabellen
# 4. 03_AI - AI Tabellen
# 5. 04_Analytics - Analytics
# 6. 05_Gamification - Gamification
# 7. 06_LiveRoom - LiveRoom
# 8. 07_Notifications - Notifications
# 9. 08_Storage - Storage
# 10. 09_Billing - Billing
# 11. 10_Community - Community
# 12. 11_System (inkl. i18n subfolder)
# 13. 12_Social - Social Network
# 14. 00_Seeds - Seed-Daten (ZULETZT!)
```

---

## Emergency Rollbacks

Verfügbar in `_emergency_rollbacks/`:
- `_999_rollback_group_system.sql` - Group System Rollback

---

## Dokumentation

- `MIGRATION_GAPS.md` - Dokumentierte Lücken in Nummerierung
- `SCHEMA_MAPPING.md` - Schema-Zuordnung
- `verify_schema.sql` - Schema-Verifikation

---

*Stand: Januar 2026*
