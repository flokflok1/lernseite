-- ============================================================================
-- Migration: 043_extend_audit_logs.sql
-- Description: Extend audit_logs table for comprehensive admin audit logging
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-11-19
-- Related: Phase B24 - Admin System
-- ============================================================================

-- ============================================================================
-- EXTEND: audit_logs table
-- Add missing columns for comprehensive audit logging
-- ============================================================================

-- Add event_category column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'audit_logs' AND column_name = 'event_category'
    ) THEN
        ALTER TABLE audit_logs ADD COLUMN event_category VARCHAR(50);
    END IF;
END$$;

-- Add user_email column (for failed logins where user_id is NULL)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'audit_logs' AND column_name = 'user_email'
    ) THEN
        ALTER TABLE audit_logs ADD COLUMN user_email VARCHAR(255);
    END IF;
END$$;

-- Add user_role column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'audit_logs' AND column_name = 'user_role'
    ) THEN
        ALTER TABLE audit_logs ADD COLUMN user_role VARCHAR(50);
    END IF;
END$$;

-- Add session_id column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'audit_logs' AND column_name = 'session_id'
    ) THEN
        ALTER TABLE audit_logs ADD COLUMN session_id VARCHAR(255);
    END IF;
END$$;

-- Add description column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'audit_logs' AND column_name = 'description'
    ) THEN
        ALTER TABLE audit_logs ADD COLUMN description TEXT;
    END IF;
END$$;

-- Add success column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'audit_logs' AND column_name = 'success'
    ) THEN
        ALTER TABLE audit_logs ADD COLUMN success BOOLEAN DEFAULT TRUE;
    END IF;
END$$;

-- Add error_message column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'audit_logs' AND column_name = 'error_message'
    ) THEN
        ALTER TABLE audit_logs ADD COLUMN error_message TEXT;
    END IF;
END$$;

-- Drop restrictive constraint on action column (to allow admin.* actions)
ALTER TABLE audit_logs DROP CONSTRAINT IF EXISTS chk_audit_action;

-- Update severity constraint to ensure it's correct
ALTER TABLE audit_logs DROP CONSTRAINT IF EXISTS chk_audit_severity;
ALTER TABLE audit_logs ADD CONSTRAINT chk_audit_severity
    CHECK (severity IN ('debug', 'info', 'warning', 'error', 'critical'));

-- Add indexes for new columns
CREATE INDEX IF NOT EXISTS idx_audit_logs_event_category ON audit_logs(event_category, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_email ON audit_logs(user_email, created_at DESC) WHERE user_email IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_audit_logs_session ON audit_logs(session_id) WHERE session_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_audit_logs_success ON audit_logs(success, created_at DESC) WHERE success = FALSE;

-- ============================================================================
-- End of Migration: 043_extend_audit_logs.sql
-- ============================================================================
