-- ============================================================================
-- MIGRATION 067: Learning Methods Plugin System
-- Date: 2026-01-11
-- Description: Adds plugin architecture for dynamic Learning Methods
-- ============================================================================

-- Table 1: lm_plugins (Main plugin metadata)
CREATE TABLE IF NOT EXISTS learning_methods.lm_plugins (
    plugin_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plugin_code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    group_code VARCHAR(1) CHECK (group_code IN ('A', 'B', 'C')),
    tier VARCHAR(20) CHECK (tier IN ('basic', 'premium', 'pro')),
    ki_usage VARCHAR(20) CHECK (ki_usage IN ('intensive', 'medium', 'optional')),
    icon VARCHAR(50),

    -- JSON Schema for plugin configuration
    config_schema JSONB NOT NULL,
    default_config JSONB,

    -- Approval workflow
    approval_status VARCHAR(20) DEFAULT 'pending_review'
        CHECK (approval_status IN ('pending_review', 'approved', 'rejected', 'in_revision', 'deprecated')),
    is_active BOOLEAN DEFAULT FALSE,

    -- File integrity
    file_path VARCHAR(500) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,

    -- Agent support (optional)
    agent_support JSONB,
    prompt_template VARCHAR(100),

    -- Audit fields
    submitted_by UUID REFERENCES core.users(user_id),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_by UUID REFERENCES core.users(user_id),
    reviewed_at TIMESTAMP,
    activated_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_lm_plugins_status ON learning_methods.lm_plugins(approval_status);
CREATE INDEX IF NOT EXISTS idx_lm_plugins_active ON learning_methods.lm_plugins(is_active);
CREATE INDEX IF NOT EXISTS idx_lm_plugins_code ON learning_methods.lm_plugins(plugin_code);

-- Table 2: lm_plugin_approval_history (Audit trail)
CREATE TABLE IF NOT EXISTS learning_methods.lm_plugin_approval_history (
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plugin_id UUID REFERENCES learning_methods.lm_plugins(plugin_id) ON DELETE CASCADE,
    action VARCHAR(20) NOT NULL
        CHECK (action IN ('submitted', 'approved', 'rejected', 'activated', 'deactivated', 'deprecated')),
    actor_id UUID REFERENCES core.users(user_id),
    reason TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_lm_plugin_history_plugin ON learning_methods.lm_plugin_approval_history(plugin_id);

-- Table 3: lm_plugin_usage (Prevent deletion of in-use plugins)
CREATE TABLE IF NOT EXISTS learning_methods.lm_plugin_usage (
    usage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plugin_id UUID REFERENCES learning_methods.lm_plugins(plugin_id) ON DELETE CASCADE,
    lesson_id UUID REFERENCES courses.lessons(lesson_id) ON DELETE CASCADE,
    method_instance_id UUID REFERENCES learning_methods.learning_method_instances(method_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(plugin_id, lesson_id)
);

CREATE INDEX IF NOT EXISTS idx_lm_plugin_usage_plugin ON learning_methods.lm_plugin_usage(plugin_id);

-- Extend learning_method_types table
ALTER TABLE learning_methods.learning_method_types
ADD COLUMN IF NOT EXISTS plugin_id UUID REFERENCES learning_methods.lm_plugins(plugin_id),
ADD COLUMN IF NOT EXISTS is_builtin BOOLEAN DEFAULT TRUE;

-- Update constraint to allow plugin LMs (method_type >= 100)
ALTER TABLE learning_methods.learning_method_types
DROP CONSTRAINT IF EXISTS chk_method_type;

ALTER TABLE learning_methods.learning_method_types
ADD CONSTRAINT chk_method_type
CHECK ((method_type >= 0 AND method_type <= 11) OR (method_type >= 100));

-- Migration complete
COMMENT ON TABLE learning_methods.lm_plugins IS 'Learning Methods Plugin metadata and approval workflow';
COMMENT ON TABLE learning_methods.lm_plugin_approval_history IS 'Audit trail for plugin approval state changes';
COMMENT ON TABLE learning_methods.lm_plugin_usage IS 'Tracks plugin usage in lessons to prevent deletion';
