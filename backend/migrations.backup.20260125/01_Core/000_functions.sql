-- ============================================================================
-- Migration: 000_functions.sql
-- Description: Common PostgreSQL functions used across all migrations
-- Category: Core Infrastructure
-- Dependencies: None (must run first!)
-- ============================================================================

-- Function: update_updated_at_column()
-- Purpose: Automatically update the 'updated_at' timestamp on row updates
-- Usage: CREATE TRIGGER ... BEFORE UPDATE ... EXECUTE FUNCTION update_updated_at_column();
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
