# Schema Migration Mapping

**Ziel:** Alle 141 Tabellen aus `public` in die korrekten Schemas verschieben

## Schema-Zuordnung

### ai_pipeline (19 Tabellen → 32 Tabellen)
```
BEREITS IM SCHEMA (6):
- ai_jobs
- ai_model_profiles
- ai_models
- ai_providers
- ki_requests
- prompt_templates

NEU VERSCHIEBEN (26):
- ai_authoring_sessions
- ai_authoring_templates
- ai_feedback
- ai_generation_variants
- ai_job_steps
- ai_prompt_learning_method_mapping
- ai_prompt_versions
- ai_prompts
- ai_provider_health
- ai_session_snapshots
- ai_studio_analytics
- ai_token_usage
- ai_usage_aggregates
- generated_theory_sheets
- ki_recommendations
- prompt_template_usage
```

### courses (11 Tabellen → 19 Tabellen)
```
BEREITS IM SCHEMA (11):
- chapter_theory
- chapters
- course_access
- course_ai_settings
- course_authoring_sessions
- course_categories
- course_enrollments
- course_files
- course_prompts
- courses
- lessons

NEU VERSCHIEBEN (8):
- chapter_progress
- chapter_resources
- class_enrollments
- content_versions
- course_collaborators
- course_features
- course_reviews
- lesson_completions
```

### learning_methods (5 Tabellen → 23 Tabellen)
```
BEREITS IM SCHEMA (5):
- authoring_actions
- capability_slots
- learning_method_instances
- learning_method_progress
- learning_method_types

NEU VERSCHIEBEN (18):
- authoring_action_usage
- learning_journals
- learning_method_executions
- learning_method_model_assignments
- learning_method_model_requirements
- learning_streaks
- lm_slot_assignments
- lm_slot_requirements
- math_calculation_steps
- math_calculator_history
- math_formulas
- math_pattern_categories
- math_pattern_recognition_tasks
- math_patterns
- math_scaffolding_hints
- math_toolkit_sessions
- math_user_progress
- spaced_repetition_items
```

### core (11 Tabellen → 29 Tabellen)
```
BEREITS IM SCHEMA (11):
- audit_logs
- config_lookup_types
- config_lookup_values
- permissions
- role_permissions
- roles
- system_config
- system_settings
- user_preferences
- user_sessions
- users

NEU VERSCHIEBEN (18):
- api_clients
- api_keys
- api_request_logs
- api_routes
- api_webhooks
- blocked_ips
- change_history
- data_access_logs
- email_verification_tokens
- feature_flags
- login_attempts
- maintenance_windows
- migration_history
- password_reset_tokens
- rate_limit_hits
- rate_limits
- security_audit_logs
- two_factor_backups
- organisations (ACHTUNG: Hat eigenes Schema!)
- organization_* Tabellen → in organisations schema!
- user_permissions
- user_profiles
```

### assessments (5 Tabellen → 10 Tabellen)
```
BEREITS IM SCHEMA (5):
- exam_questions
- exam_results
- exam_simulations
- exam_submission_snapshots
- exams

NEU VERSCHIEBEN (5):
- certificate_requirements
- certificate_templates
- exam_answers
- exam_attempts
- exam_simulation_attempts
```

### support_systems (11 Tabellen → 15 Tabellen)
```
BEREITS IM SCHEMA (11):
- error_logs
- faqs
- feedback
- knowledge_base_articles
- support_categories
- support_tickets
- ticket_comments
- ticket_history
- ticket_priorities
- ticket_statuses
- user_reports

NEU VERSCHIEBEN (4):
- feedback_attachments
- feedback_notes
- feedback_summary_batches
- user_feedback
```

### translations (1 Tabelle → 13 Tabellen)
```
BEREITS IM SCHEMA (1):
- translations

NEU VERSCHIEBEN (12):
- i18n_ai_config
- i18n_ai_reviews
- i18n_keys
- i18n_moderation_queue
- i18n_namespaces
- i18n_suggestion_votes
- i18n_suggestions
- i18n_translation_requests
- i18n_translations
- supported_languages
- translation_cache
- tts_ai_requests
- tts_pronunciations
```

### liveroom (6 Tabellen → 10 Tabellen)
```
BEREITS IM SCHEMA (6):
- room_participants
- room_recordings
- room_transcripts
- room_whiteboards
- rooms
- room_ai_stats

NEU VERSCHIEBEN (4):
- room_logs
- tutor_agent_configs
- tutor_interactions
- tutor_sessions
- tutor_messages (PRÜFEN: gibt es die?)
```

### billing_storage (6 Tabellen → 10 Tabellen)
```
BEREITS IM SCHEMA (6):
- invoices
- storage_quotas
- subscription_plans
- subscriptions
- token_transactions
- token_wallets

NEU VERSCHIEBEN (4):
- payment_history
- quota_usage
- subscription_changes
```

### smart_agents (3 Tabellen → 11 Tabellen)
```
BEREITS IM SCHEMA (3):
- agent_capabilities
- agent_execution_history
- agents

NEU VERSCHIEBEN (8):
- agent_cache_entries
- agent_org_extensions
- agent_query_log
- agent_realtime_sessions
- agent_transcript_cache
- agent_tts_cache
- agent_video_cache
- agent_warm_jobs
```

### NEUE SCHEMAS

#### gamification (neu - 7 Tabellen)
```
- gamification_progress
- learning_streaks (ODER learning_methods?)
- skill_endorsements
- user_achievements
- user_skills
- user_xp
- xp_transactions
```

#### community (neu - 13 Tabellen)
```
- group_discussions
- group_messages
- group_posts
- peer_review_ratings
- peer_review_submissions
- peer_review_tasks
- portfolio_items
- team_case_members
- team_case_teams
- team_cases
```

#### organisations (prüfen - 6 Tabellen)
```
PRÜFEN ob Schema existiert, sonst anlegen:
- organization_branding
- organization_classes
- organization_features
- organization_members (existiert vermutlich schon)
- organization_quotas
- organization_settings (existiert vermutlich schon)
- organisations
```

#### notifications (neu - 3 Tabellen)
```
- notification_channels
- notification_logs
- notification_templates
```

#### storage (neu - 4 Tabellen)
```
- file_versions
- media_thumbnails
- pdf_cache
```

#### dashboards (neu - 4 Tabellen)
```
- dashboard_layouts
- user_widgets
- widget_access_log
- widget_data_cache
- widgets
```

#### it_environments (neu - 1 Tabelle)
```
- it_sandbox_instances
```

#### email (neu - 1 Tabelle)
```
- email_queue
```

### IM PUBLIC BLEIBEN (1 Tabelle)
```
- migration_history (muss in public bleiben für Setup Wizard)
- system_feature_types (könnte in core, aber public ist ok)
```

## Zusammenfassung

| Schema | Aktuell | Ziel | Differenz |
|--------|---------|------|-----------|
| ai_pipeline | 6 | 32 | +26 |
| courses | 11 | 19 | +8 |
| learning_methods | 5 | 23 | +18 |
| core | 11 | 29 | +18 |
| assessments | 5 | 10 | +5 |
| support_systems | 11 | 15 | +4 |
| translations | 1 | 13 | +12 |
| liveroom | 6 | 10 | +4 |
| billing_storage | 6 | 10 | +4 |
| smart_agents | 3 | 11 | +8 |
| agent_intelligence | 4 | 4 | 0 |
| **gamification** (neu) | 0 | 7 | +7 |
| **community** (neu) | 0 | 13 | +13 |
| **organisations** | ? | 7 | ? |
| **notifications** (neu) | 0 | 3 | +3 |
| **storage** (neu) | 0 | 4 | +4 |
| **dashboards** (neu) | 0 | 4 | +4 |
| **it_environments** (neu) | 0 | 1 | +1 |
| **email** (neu) | 0 | 1 | +1 |
| **public** | 141 | 2 | -139 |

**Total:** 211 Tabellen bleiben 211 Tabellen, nur besser organisiert!
