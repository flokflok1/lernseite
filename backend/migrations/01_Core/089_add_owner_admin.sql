-- ============================================================================
-- Migration: 089_add_owner_admin.sql
-- Description: Add is_owner field to users table (Enable Owner-Admin functionality)
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-16
-- ============================================================================
-- Previous number: 067 (Root) → Renumbered to 089 to resolve duplicates
-- Purpose: Enable Owner-Admin functionality

-- Add is_owner column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_owner BOOLEAN DEFAULT FALSE;

-- Create unique partial index to ensure only one owner exists
CREATE UNIQUE INDEX IF NOT EXISTS idx_single_owner ON users(is_owner) WHERE is_owner = TRUE;

-- Add comment
COMMENT ON COLUMN users.is_owner IS 'Owner-Admin flag - only one user can be owner';

