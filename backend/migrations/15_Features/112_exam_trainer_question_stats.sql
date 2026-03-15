-- ============================================================================
-- Migration: 112_exam_trainer_question_stats.sql
-- Description: Per-question per-user tracking for intelligent rotation
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-03-15
-- ============================================================================

-- Tracks how often each user has seen/answered each question.
-- Drives the rotation algorithm: unseen → weak → spaced review → random.
CREATE TABLE IF NOT EXISTS assessments.user_question_stats (
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES assessments.exam_questions(question_id) ON DELETE CASCADE,

    times_seen INTEGER NOT NULL DEFAULT 0,
    times_correct INTEGER NOT NULL DEFAULT 0,
    last_seen_at TIMESTAMPTZ,
    last_correct_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (user_id, question_id)
);

-- Index: find questions a user has NOT seen (anti-join pattern)
CREATE INDEX IF NOT EXISTS idx_uqs_user
    ON assessments.user_question_stats (user_id);

-- Index: find weak questions (seen but rarely correct)
CREATE INDEX IF NOT EXISTS idx_uqs_user_weak
    ON assessments.user_question_stats (user_id, times_seen, times_correct)
    WHERE times_seen > 0 AND times_correct < times_seen;
