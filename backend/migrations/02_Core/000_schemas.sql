-- ============================================================================
-- Migration: 000_schemas.sql
-- Version: 1.0.0
-- Description: Create ALL database schemas (Phase 0 - Foundation)
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- Dependencies: None (this runs FIRST)
-- ============================================================================
-- IMPORTANT: This migration MUST run first before all other migrations!
-- It creates all database schemas that other migrations will populate with tables.
-- ============================================================================

-- ============================================================================
-- Core Schemas (User Management, Auth, Permissions)
-- ============================================================================
CREATE SCHEMA IF NOT EXISTS core;
COMMENT ON SCHEMA core IS 'Core domain: Users, Roles, Permissions, Authentication, Audit Logs';

CREATE SCHEMA IF NOT EXISTS organisations;
COMMENT ON SCHEMA organisations IS 'Organizations domain: Schools, Companies, Teams, Memberships';

-- ============================================================================
-- Content & Learning Schemas
-- ============================================================================
CREATE SCHEMA IF NOT EXISTS courses;
COMMENT ON SCHEMA courses IS 'Content domain: Courses, Chapters, Lessons, Learning Methods';

CREATE SCHEMA IF NOT EXISTS learning_methods;
COMMENT ON SCHEMA learning_methods IS 'Learning Methods: 12 Content-LMs (LM00-LM11) and system configuration';

-- ============================================================================
-- AI & Intelligence Schemas
-- ============================================================================
CREATE SCHEMA IF NOT EXISTS ai_pipeline;
COMMENT ON SCHEMA ai_pipeline IS 'AI domain: Models, Jobs, Prompts, Recommendations, KI Pipeline';

CREATE SCHEMA IF NOT EXISTS agent_intelligence;
COMMENT ON SCHEMA agent_intelligence IS 'AI Agents domain: Agent configurations, knowledge bases, routing';

-- ============================================================================
-- Billing & Storage Schemas
-- ============================================================================
CREATE SCHEMA IF NOT EXISTS billing_storage;
COMMENT ON SCHEMA billing_storage IS 'Billing domain: Subscriptions, Payments, Transactions, Media Files, Storage';

-- ============================================================================
-- System-Features Schema (Separate from Content-Lernmethoden!)
-- ============================================================================
CREATE SCHEMA IF NOT EXISTS system_features;
COMMENT ON SCHEMA system_features IS 'System-Features domain: 25 Infrastructure Tools/Services (whiteboard_engine, code_sandbox, math_patterns, etc.) - SEPARATE from Content-Lernmethoden (LM00-LM11)';

-- ============================================================================
-- Community & Collaboration Schemas
-- ============================================================================
CREATE SCHEMA IF NOT EXISTS support_systems;
COMMENT ON SCHEMA support_systems IS 'Community domain: Groups, Feedback, Tutor System, Support';

-- ============================================================================
-- Dashboard & Specialized Feature Schemas
-- ============================================================================
CREATE SCHEMA IF NOT EXISTS dashboards;
COMMENT ON SCHEMA dashboards IS 'Dashboard domain: Widgets, Layouts, Caching, Analytics';

CREATE SCHEMA IF NOT EXISTS analytics;
COMMENT ON SCHEMA analytics IS 'Analytics domain: System metrics, User behavior, Performance tracking';

CREATE SCHEMA IF NOT EXISTS translations;
COMMENT ON SCHEMA translations IS 'Internationalization: Translated strings, i18n management';

-- ============================================================================
-- Verification
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE '✓ Migration 000 completed successfully - 12 schemas created';
    RAISE NOTICE '  Schemas: core, organisations, courses, learning_methods, ai_pipeline,';
    RAISE NOTICE '           agent_intelligence, billing_storage, system_features,';
    RAISE NOTICE '           support_systems, dashboards, analytics, translations';
END $$;
