-- ============================================================================
-- Migration: 000_functions.sql
-- Description: Common PostgreSQL functions used across all migrations
-- Category: Core Infrastructure
-- Dependencies: None (must run first!)
-- ============================================================================

-- ============================================================================
-- REQUIRED EXTENSIONS
-- These must be created before any migration uses UUID generation
-- ============================================================================

-- uuid-ossp: Provides uuid_generate_v4() function
-- Used by: 002_security_auth, 003_organisations, 005_api_gateway, and 20+ other migrations
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- pgcrypto: Provides gen_random_uuid() and cryptographic functions
-- Used by: 001_users_table (gen_random_uuid), password hashing
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- COMMON FUNCTIONS
-- ============================================================================

-- Function: update_updated_at_column()
-- Purpose: Automatically update the 'updated_at' timestamp on row updates
-- Usage: CREATE TRIGGER ... BEFORE UPDATE ... EXECUTE FUNCTION update_updated_at_column();
-- Note: Created in public schema for global access. Can be referenced as:
--       - update_updated_at_column() (implicit public)
--       - public.update_updated_at_column() (explicit)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- End of Migration: 000_functions.sql
-- ============================================================================
