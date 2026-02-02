-- ============================================================================
-- Migration: 000_schemas.sql
-- Description: Create all database schemas (MUST RUN FIRST)
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-27
-- ============================================================================
-- WICHTIG: Diese Migration MUSS vor allen anderen laufen!
-- Sie erstellt alle Schemas, die von anderen Migrations verwendet werden.
-- ============================================================================

BEGIN;

-- ============================================================================
-- Core Schemas
-- ============================================================================
CREATE SCHEMA IF NOT EXISTS core;
COMMENT ON SCHEMA core IS 'Core system: Users, Authentication, Organizations, Groups';

CREATE SCHEMA IF NOT EXISTS organisations;
COMMENT ON SCHEMA organisations IS 'Multi-tenancy: Organizations, members, settings';

-- ============================================================================
-- Content Schemas
-- ============================================================================
CREATE SCHEMA IF NOT EXISTS courses;
COMMENT ON SCHEMA courses IS 'Learning content: Courses, chapters, lessons, enrollments';

CREATE SCHEMA IF NOT EXISTS learning_methods;
COMMENT ON SCHEMA learning_methods IS 'Learning method types and instances (12 LM00-LM11)';

-- ============================================================================
-- Feature Schemas
-- ============================================================================
CREATE SCHEMA IF NOT EXISTS gamification;
COMMENT ON SCHEMA gamification IS 'Gamification: XP, badges, achievements, streaks';

CREATE SCHEMA IF NOT EXISTS support_systems;
COMMENT ON SCHEMA support_systems IS 'System features: Whiteboard, code sandbox, livestream, etc.';

CREATE SCHEMA IF NOT EXISTS analytics;
COMMENT ON SCHEMA analytics IS 'Analytics: Events, user behavior, statistics';

CREATE SCHEMA IF NOT EXISTS ai_pipeline;
COMMENT ON SCHEMA ai_pipeline IS 'AI: Models, jobs, prompts, usage tracking';

CREATE SCHEMA IF NOT EXISTS ai;
COMMENT ON SCHEMA ai IS 'AI system: Preferred naming for AI-related tables. Use this or ai_pipeline for new AI features (ACTIVE)';

CREATE SCHEMA IF NOT EXISTS liveroom;
COMMENT ON SCHEMA liveroom IS 'LiveRoom: WebRTC rooms, chat, whiteboard, recordings';

CREATE SCHEMA IF NOT EXISTS notifications;
COMMENT ON SCHEMA notifications IS 'Notifications system';

CREATE SCHEMA IF NOT EXISTS media;
COMMENT ON SCHEMA media IS 'RESERVED: Media storage - currently unused, see storage and billing_storage schemas';

CREATE SCHEMA IF NOT EXISTS billing;
COMMENT ON SCHEMA billing IS 'RESERVED: Billing - currently unused, see billing_storage schema for active billing tables';

CREATE SCHEMA IF NOT EXISTS billing_storage;
COMMENT ON SCHEMA billing_storage IS 'Billing & Media storage: subscriptions, payments, tokens, media_files (ACTIVE - primary billing schema)';

CREATE SCHEMA IF NOT EXISTS storage;
COMMENT ON SCHEMA storage IS 'Storage infrastructure: File versions, thumbnails, packages, virus scanning (ACTIVE)';

CREATE SCHEMA IF NOT EXISTS smart_agents;
COMMENT ON SCHEMA smart_agents IS 'Smart agent system: Course agents, knowledge bases, caching, query logs (ACTIVE)';

CREATE SCHEMA IF NOT EXISTS agent_intelligence;
COMMENT ON SCHEMA agent_intelligence IS 'Agent intelligence: Domain taxonomy, knowledge pooling, cross-agent learning (ACTIVE)';

CREATE SCHEMA IF NOT EXISTS community;
COMMENT ON SCHEMA community IS 'Community features: Group discussions, forums, direct messages (ACTIVE)';

CREATE SCHEMA IF NOT EXISTS social;
COMMENT ON SCHEMA social IS 'Social network: Posts, follows, likes, comments, shares, hashtags (ACTIVE)';

CREATE SCHEMA IF NOT EXISTS exams;
COMMENT ON SCHEMA exams IS 'RESERVED: Examination system - currently unused, tables in assessments schema';

CREATE SCHEMA IF NOT EXISTS assessments;
COMMENT ON SCHEMA assessments IS 'Assessment system: Exams, questions, results, certificates (ACTIVE - use this for exam tables)';

CREATE SCHEMA IF NOT EXISTS compliance;
COMMENT ON SCHEMA compliance IS 'Compliance: GDPR, DSA, NetzDG, age verification';

CREATE SCHEMA IF NOT EXISTS moderation;
COMMENT ON SCHEMA moderation IS 'Content moderation: Reports, appeals, actions';

CREATE SCHEMA IF NOT EXISTS audit;
COMMENT ON SCHEMA audit IS 'RESERVED: Audit logging - currently unused, see core.audit_logs table';

CREATE SCHEMA IF NOT EXISTS ki;
COMMENT ON SCHEMA ki IS 'DEPRECATED: Legacy KI schema - use ai_pipeline for all AI tables. Kept for backward compatibility only.';

CREATE SCHEMA IF NOT EXISTS translations;
COMMENT ON SCHEMA translations IS 'Translations: i18n strings, localization';

CREATE SCHEMA IF NOT EXISTS email;
COMMENT ON SCHEMA email IS 'RESERVED: Email system - currently unused, planned for email queues and templates';

CREATE SCHEMA IF NOT EXISTS dashboards;
COMMENT ON SCHEMA dashboards IS 'Dashboard widgets and configurations';
COMMIT;


