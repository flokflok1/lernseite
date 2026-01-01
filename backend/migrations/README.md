# Database Migrations

> **68 Migrations** in **11 Kategorien** - PostgreSQL Schema für LernsystemX

---

## Ordnerstruktur

| Ordner | Anzahl | Beschreibung |
|--------|--------|--------------|
| [01_Core](#01_core) | 9 | Users, Roles, Security, Organisations, Preferences |
| [02_Content](#02_content) | 19 | Courses, Chapters, Lessons, LMs, Exams, Categories |
| [03_AI](#03_ai) | 18 | Providers, Models, Prompts, Agents, TTS, Authoring |
| [04_Analytics](#04_analytics) | 3 | Analytics, Events, Feedback |
| [05_Gamification](#05_gamification) | 2 | XP, Badges |
| [06_LiveRoom](#06_liveroom) | 2 | Rooms, Chat |
| [07_Notifications](#07_notifications) | 3 | Notifications, Templates |
| [08_Storage](#08_storage) | 3 | Media Files, Cache |
| [09_Billing](#09_billing) | 3 | Subscriptions, Transactions |
| [10_Community](#10_community) | 2 | Groups, Messages |
| [11_System](#11_system) | 4 | Translations, Rate Limits, System Features |

---

## 01_Core

Users, Authentifizierung, Organisationen, Einstellungen.

| Nr | Datei | Beschreibung |
|----|-------|--------------|
| 001 | core_users_roles | users, roles, permissions |
| 002 | security_auth | sessions, tokens |
| 003 | organisations | organisations, org_members |
| 004 | organisation_settings | org_settings, branding |
| 005 | api_gateway | api_keys, api_logs |
| 006 | audit_logging | audit_logs |
| 007 | system_settings | system_settings, flags |
| 042 | add_theme_preference | User Theme Einstellungen |
| 051 | user_preferences | User Preferences JSONB |

---

## 02_Content

Kurse, Kapitel, Lektionen, Lernmethoden, Prüfungen.

| Nr | Datei | Beschreibung |
|----|-------|--------------|
| 008 | courses | courses, enrollments |
| 009 | chapters | chapters |
| 010 | lessons | lessons, content |
| 011 | learning_methods | lm_instances |
| 012 | learning_progress | progress, completions |
| 013 | exams | exams, questions |
| 014 | exam_results | attempts, scores |
| 015 | certificates | certificates, templates |
| 016 | certificates_progress | cert_progress |
| 041 | learning_method_types | LM-Typen Tabelle |
| 043 | course_prompts | Kurs-Prompt Overrides |
| 044 | course_files | Datei-Anhänge |
| 046 | rename_modules_to_chapters | Module→Chapter Refactoring |
| 047 | learning_methods_module_to_chapter | LM Module→Chapter |
| 049 | flexible_categories | Hierarchische Kategorien |
| 054 | lm_refactoring_and_features | LM Refactoring |
| 062 | **lm_19_content_methods** | **19 Content-LMs (aktuell)** |
| 064 | math_toolkit | Math Toolkit |
| 065 | exam_simulation_tables | Prüfungssimulation |

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
| 048 | ai_authoring_studio | Authoring Studio |
| 050 | ai_models_sync_support | API Sync für Models |
| 052 | learning_method_model_routing | LM Model Routing |
| 053 | capability_slots | AI Capability Slots |
| 055 | smart_agent_system | Smart Agent System |
| 058 | learning_method_ai_tables | LM AI Tables |
| 059 | tts_pronunciation | TTS Aussprache |
| 060 | prompt_templates | Prompt Template System |
| 061 | authoring_actions | Authoring Actions |
| 066 | course_authoring_sessions | Authoring Sessions |
| 067 | course_ai_settings | Course AI Settings |
| 068 | ai_model_profiles_base | AI Model Profiles |

---

## 04_Analytics

Analytics, Events, Feedback.

| Nr | Datei | Beschreibung |
|----|-------|--------------|
| 022 | analytics_core | metrics, dashboards |
| 023 | analytics_events | events, aggregations |
| 057 | feedback_system | Feedback Tables |

---

## 05_Gamification

| Nr | Datei | Beschreibung |
|----|-------|--------------|
| 024 | gamification | xp, levels, streaks |
| 025 | badges | badges, user_badges |

---

## 06_LiveRoom

| Nr | Datei | Beschreibung |
|----|-------|--------------|
| 026 | liverooms_core | rooms, participants |
| 027 | liverooms_chat | messages, whiteboards |

---

## 07_Notifications

| Nr | Datei | Beschreibung |
|----|-------|--------------|
| 028 | notifications_core | notifications |
| 029 | notifications_templates | templates |
| 030 | notifications_logs | delivery_logs |

---

## 08_Storage

| Nr | Datei | Beschreibung |
|----|-------|--------------|
| 031 | media_files | files, metadata |
| 032 | storage_versions | versions, cleanup |
| 056 | agent_media_cache | Agent Media Cache |

---

## 09_Billing

| Nr | Datei | Beschreibung |
|----|-------|--------------|
| 033 | billing_core | plans, pricing |
| 034 | billing_subscriptions | subscriptions, tokens |
| 035 | billing_transactions | transactions, invoices |

---

## 10_Community

| Nr | Datei | Beschreibung |
|----|-------|--------------|
| 036 | community_core | groups, memberships |
| 037 | community_messages | posts, comments |

---

## 11_System

| Nr | Datei | Beschreibung |
|----|-------|--------------|
| 038 | translations | translations, locales |
| 039 | rate_limits | rate_limits, quotas |
| 040 | integrity_checks | constraints, triggers |
| 063 | system_features_tables | System Features |

---

## Archiviert

Veraltete Migrations in `backend/_archive/old_database_migrations/`:
- `046_add_gpt5_models.sql` - Fake GPT-5 Models (ersetzt durch API-Sync)
- `047_learning_methods_32.sql` - Alte 32-LM Version (ersetzt durch 062)

---

*Stand: Dezember 2024*
