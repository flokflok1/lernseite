-- ============================================================================
-- Seed Data: System Configuration & Lookup Types/Values
-- Description: System configuration, lookup types and values for all domains
-- Source: 099_config_system.sql
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 4 (Seed Data - runs AFTER all structural migrations)
-- ============================================================================

-- Insert lookup types (metadata about enum-like values)

-- Learning Methods
INSERT INTO core.config_lookup_types (type_code, type_name, description, table_name, column_name) VALUES
    ('lm_group_code', 'Learning Method Groups', 'Groups A-C for learning methods', 'learning_methods.learning_method_types', 'group_code'),
    ('lm_tier', 'Learning Method Tiers', 'basic, premium, pro', 'learning_methods.learning_method_types', 'tier'),
    ('lm_ki_usage', 'AI Usage Intensity', 'intensive, medium, optional', 'learning_methods.learning_method_types', 'ki_usage'),
    ('lm_difficulty', 'Difficulty Levels', 'easy, medium, hard', 'learning_methods.learning_method_instances', 'difficulty')
ON CONFLICT DO NOTHING;

-- Subscriptions & Billing
INSERT INTO core.config_lookup_types (type_code, type_name, description, table_name, column_name) VALUES
    ('subscription_plan', 'Subscription Plans', 'free, premium, creator, teacher, school, company', 'billing_storage.subscriptions', 'plan_type'),
    ('subscription_status', 'Subscription Status', 'active, past_due, canceled, trialing, etc.', 'billing_storage.subscriptions', 'status'),
    ('billing_cycle', 'Billing Cycles', 'monthly, yearly', 'billing_storage.subscriptions', 'billing_cycle'),
    ('payment_type', 'Payment Methods', 'card, sepa_debit, paypal, invoice', 'billing_storage.payment_methods', 'payment_type'),
    ('payment_status', 'Payment Status', 'pending, succeeded, failed, refunded', 'billing_storage.payments', 'status'),
    ('token_transaction_type', 'Token Transaction Types', 'grant, purchase, consumption, refund', 'billing_storage.token_transactions', 'transaction_type')
ON CONFLICT DO NOTHING;

-- AI Pipeline
INSERT INTO core.config_lookup_types (type_code, type_name, description, table_name, column_name) VALUES
    ('ai_provider_type', 'AI Provider Types', 'openai, anthropic, google, etc.', 'ai_pipeline.ai_providers', 'provider_type'),
    ('ai_model_type', 'AI Model Types', 'completion, chat, embedding, vision', 'ai_pipeline.ai_models', 'model_type'),
    ('ai_prompt_category', 'AI Prompt Categories', 'chapter_generation, method_generation, etc.', 'ai_pipeline.ai_prompts', 'category'),
    ('ai_job_status', 'AI Job Status', 'queued, processing, completed, failed', 'ai_pipeline.ai_jobs', 'status'),
    ('ai_provider_health', 'Provider Health Status', 'healthy, degraded, down', 'ai_pipeline.ai_provider_health', 'status')
ON CONFLICT DO NOTHING;

-- Notifications
INSERT INTO core.config_lookup_types (type_code, type_name, description, table_name, column_name) VALUES
    ('notification_type', 'Notification Types', 'system, course, exam, achievement', 'support_systems.notifications', 'notification_type'),
    ('notification_priority', 'Notification Priority', 'low, normal, high, urgent', 'support_systems.notifications', 'priority'),
    ('notification_channel', 'Notification Channels', 'email, push, sms, in_app', 'support_systems.notification_preferences', 'channel'),
    ('notification_frequency', 'Notification Frequency', 'realtime, hourly, daily, weekly', 'support_systems.notification_preferences', 'frequency')
ON CONFLICT DO NOTHING;

-- Community
INSERT INTO core.config_lookup_types (type_code, type_name, description, table_name, column_name) VALUES
    ('group_type', 'Group Types', 'study, project, course, interest', 'organisations.groups', 'group_type'),
    ('group_member_role', 'Group Member Roles', 'owner, admin, moderator, member', 'organisations.group_members', 'role'),
    ('group_resource_type', 'Group Resource Types', 'file, link, course_copy, note', 'organisations.group_resources', 'resource_type')
ON CONFLICT DO NOTHING;

-- Gamification
INSERT INTO core.config_lookup_types (type_code, type_name, description, table_name, column_name) VALUES
    ('badge_type', 'Badge Types', 'achievement, milestone, special, seasonal', 'analytics.badges', 'badge_type'),
    ('badge_tier', 'Badge Tiers', 'bronze, silver, gold, platinum, diamond', 'analytics.badges', 'tier'),
    ('leaderboard_type', 'Leaderboard Types', 'xp, courses_completed, streak, exam_score', 'analytics.leaderboards', 'leaderboard_type'),
    ('leaderboard_scope', 'Leaderboard Scope', 'global, organization, class, course', 'analytics.leaderboards', 'scope')
ON CONFLICT DO NOTHING;

-- Course & Content
INSERT INTO core.config_lookup_types (type_code, type_name, description, table_name, column_name) VALUES
    ('enrollment_status', 'Enrollment Status', 'active, completed, paused, dropped', 'courses.enrollments', 'status'),
    ('chapter_resource_type', 'Chapter Resource Types', 'pdf, video, audio, document, link', 'courses.chapter_resources', 'resource_type')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- Lookup Values (actual enum values)
-- ============================================================================

-- Learning Method Groups
INSERT INTO core.config_lookup_values (type_id, value_code, value_label, value_description, sort_order) VALUES
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'lm_group_code'), 'A', 'Erklärend', 'Verständnis aufbauen (lm00-lm04)', 1),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'lm_group_code'), 'B', 'Praxis', 'Anwenden & Üben (lm05-lm10)', 2),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'lm_group_code'), 'C', 'Prüfung', 'Prüfungsvorbereitung (lm11-lm18)', 3)
ON CONFLICT (type_id, value_code) DO NOTHING;

-- Learning Method Tiers
INSERT INTO core.config_lookup_values (type_id, value_code, value_label, value_description, sort_order, metadata) VALUES
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'lm_tier'), 'basic', 'Basic', 'Verfügbar für alle Benutzer', 1, '{"color": "blue", "icon": "user"}'),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'lm_tier'), 'premium', 'Premium', 'Nur für Premium-Nutzer', 2, '{"color": "gold", "icon": "star"}'),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'lm_tier'), 'pro', 'Pro', 'Nur für Pro-Nutzer', 3, '{"color": "purple", "icon": "crown"}')
ON CONFLICT (type_id, value_code) DO NOTHING;

-- AI Usage Intensity
INSERT INTO core.config_lookup_values (type_id, value_code, value_label, value_description, sort_order) VALUES
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'lm_ki_usage'), 'intensive', 'Intensiv', 'Vollständige KI-Generierung (1000-6000 Tokens)', 1),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'lm_ki_usage'), 'medium', 'Mittel', 'KI-Unterstützung (500-2000 Tokens)', 2),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'lm_ki_usage'), 'optional', 'Optional', 'Manuell oder KI (0-500 Tokens)', 3)
ON CONFLICT (type_id, value_code) DO NOTHING;

-- Difficulty Levels
INSERT INTO core.config_lookup_values (type_id, value_code, value_label, value_description, sort_order, metadata) VALUES
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'lm_difficulty'), 'easy', 'Einfach', 'Grundlagen & Einsteiger', 1, '{"color": "green"}'),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'lm_difficulty'), 'medium', 'Mittel', 'Fortgeschrittene Themen', 2, '{"color": "yellow"}'),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'lm_difficulty'), 'hard', 'Schwer', 'Experten-Level', 3, '{"color": "red"}')
ON CONFLICT (type_id, value_code) DO NOTHING;

-- Subscription Plans
INSERT INTO core.config_lookup_values (type_id, value_code, value_label, value_description, sort_order, metadata) VALUES
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'subscription_plan'), 'free', 'Free', 'Kostenloser Account', 1, '{"tokens_per_month": 0}'),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'subscription_plan'), 'premium', 'Premium', 'Premium-Account (10.000 Tokens)', 2, '{"tokens_per_month": 10000}'),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'subscription_plan'), 'creator', 'Creator', 'Content-Creator', 3, '{"tokens_per_month": 50000}'),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'subscription_plan'), 'teacher', 'Teacher', 'Lehrer-Account', 4, '{"tokens_per_month": 25000}'),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'subscription_plan'), 'school', 'School', 'Schul-Lizenz', 5, '{"tokens_per_month": 100000}'),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'subscription_plan'), 'company', 'Company', 'Unternehmens-Lizenz', 6, '{"tokens_per_month": 500000}')
ON CONFLICT (type_id, value_code) DO NOTHING;

-- Subscription Status
INSERT INTO core.config_lookup_values (type_id, value_code, value_label, value_description, sort_order, metadata) VALUES
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'subscription_status'), 'active', 'Aktiv', 'Subscription aktiv', 1, '{"color": "green"}'),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'subscription_status'), 'past_due', 'Überfällig', 'Zahlung überfällig', 2, '{"color": "orange"}'),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'subscription_status'), 'canceled', 'Gekündigt', 'Subscription gekündigt', 3, '{"color": "red"}'),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'subscription_status'), 'unpaid', 'Unbezahlt', 'Zahlung ausstehend', 4, '{"color": "red"}'),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'subscription_status'), 'trialing', 'Testphase', 'Im Trial-Zeitraum', 5, '{"color": "blue"}'),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'subscription_status'), 'incomplete', 'Unvollständig', 'Setup nicht abgeschlossen', 6, '{"color": "gray"}')
ON CONFLICT (type_id, value_code) DO NOTHING;

-- AI Provider Types
INSERT INTO core.config_lookup_values (type_id, value_code, value_label, value_description, sort_order) VALUES
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'ai_provider_type'), 'openai', 'OpenAI', 'GPT-4, GPT-3.5', 1),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'ai_provider_type'), 'anthropic', 'Anthropic', 'Claude Opus, Sonnet, Haiku', 2),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'ai_provider_type'), 'google', 'Google', 'Gemini Pro', 3),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'ai_provider_type'), 'cohere', 'Cohere', 'Command, Embed', 4),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'ai_provider_type'), 'huggingface', 'HuggingFace', 'Open-Source Models', 5),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'ai_provider_type'), 'ollama', 'Ollama', 'Local Models', 6),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'ai_provider_type'), 'custom', 'Custom', 'Custom API Endpoint', 7)
ON CONFLICT (type_id, value_code) DO NOTHING;

-- AI Job Status
INSERT INTO core.config_lookup_values (type_id, value_code, value_label, value_description, sort_order, metadata) VALUES
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'ai_job_status'), 'queued', 'In Warteschlange', 'Wartet auf Ausführung', 1, '{"color": "gray"}'),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'ai_job_status'), 'processing', 'Wird verarbeitet', 'Läuft gerade', 2, '{"color": "blue"}'),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'ai_job_status'), 'completed', 'Abgeschlossen', 'Erfolgreich fertig', 3, '{"color": "green"}'),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'ai_job_status'), 'failed', 'Fehlgeschlagen', 'Fehler aufgetreten', 4, '{"color": "red"}'),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'ai_job_status'), 'cancelled', 'Abgebrochen', 'Von User abgebrochen', 5, '{"color": "orange"}')
ON CONFLICT (type_id, value_code) DO NOTHING;

-- Badge Types
INSERT INTO core.config_lookup_values (type_id, value_code, value_label, value_description, sort_order, metadata) VALUES
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'badge_type'), 'achievement', 'Erfolg', 'Erfolg erreicht', 1, '{"icon": "trophy"}'),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'badge_type'), 'milestone', 'Meilenstein', 'Wichtiger Meilenstein', 2, '{"icon": "flag"}'),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'badge_type'), 'special', 'Spezial', 'Besondere Auszeichnung', 3, '{"icon": "star"}'),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'badge_type'), 'seasonal', 'Saisonal', 'Event-Badge', 4, '{"icon": "calendar"}'),
    ((SELECT type_id FROM core.config_lookup_types WHERE type_code = 'badge_type'), 'community', 'Community', 'Community-Beitrag', 5, '{"icon": "users"}')
ON CONFLICT (type_id, value_code) DO NOTHING;
