-- ============================================================================
-- Migration: 109_exam_topic_nodes.sql
-- Description: Self-referencing topic hierarchy for exam question topics
-- ============================================================================
BEGIN;

CREATE TABLE IF NOT EXISTS assessments.exam_topic_nodes (
    topic_key    VARCHAR(100) PRIMARY KEY,
    parent_key   VARCHAR(100) REFERENCES assessments.exam_topic_nodes(topic_key)
                 ON DELETE SET NULL ON UPDATE CASCADE,
    display_name JSONB NOT NULL DEFAULT '{}',
    sort_order   INTEGER DEFAULT 0,
    source       VARCHAR(20) DEFAULT 'ai'
                 CHECK (source IN ('ai', 'admin', 'import')),
    created_at   TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_exam_topic_nodes_parent
    ON assessments.exam_topic_nodes(parent_key);

COMMIT;
