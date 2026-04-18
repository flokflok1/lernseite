-- ============================================================================
-- Migration: 122_ap2_mastery_tracking.sql
-- Description: Performance-Tracking-Erweiterung für AP2 TopicMastery.
--              Drei neue Spalten erlauben Trend-Detection und Personal-Best:
--
--              - best_pct           Höchste je erreichte pct in diesem Topic
--              - best_pct_date      Wann wurde der Personal Best erreicht
--              - regression_streak  Wie viele Versuche in Folge unter best_pct - 10
--
--              Ergänzt durch View `ap2_recent_regressions` die zeigt, welche
--              Items schwächer beantwortet wurden als beim vorherigen Versuch.
--              Treibt die "Mini-Schwächen"-Sektion im Dashboard.
--
--              Asymmetrischer EMA (Domain Model): bei Verschlechterung sinkt
--              der mastery_score schneller (alpha=0.5) als er bei Verbesserung
--              steigt (alpha=0.2) — Desirable Difficulty Pattern.
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-04-18
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. NEUE SPALTEN in ap2_topic_mastery
-- ---------------------------------------------------------------------------

ALTER TABLE assessments.ap2_topic_mastery
    ADD COLUMN IF NOT EXISTS best_pct INT NOT NULL DEFAULT 0
        CHECK (best_pct BETWEEN 0 AND 100);

ALTER TABLE assessments.ap2_topic_mastery
    ADD COLUMN IF NOT EXISTS best_pct_date TIMESTAMPTZ;

ALTER TABLE assessments.ap2_topic_mastery
    ADD COLUMN IF NOT EXISTS regression_streak INT NOT NULL DEFAULT 0
        CHECK (regression_streak >= 0);

COMMENT ON COLUMN assessments.ap2_topic_mastery.best_pct IS
    'Höchste je in diesem Topic erreichte pct. Steigt monoton — wird nie reduziert.';
COMMENT ON COLUMN assessments.ap2_topic_mastery.best_pct_date IS
    'Wann wurde der Personal Best erreicht (für UX: "Du warst am 03.05. schon mal 92%").';
COMMENT ON COLUMN assessments.ap2_topic_mastery.regression_streak IS
    'Wie viele Versuche in Folge lagen mind. 10%-Punkte unter best_pct. '
    'Reset auf 0 bei pct >= best_pct - 10.';

-- ---------------------------------------------------------------------------
-- 2. VIEW: Recent Regressions auf Item-Ebene
--          Liefert Items wo der letzte Attempt schlechter war als der vorletzte
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW assessments.ap2_recent_regressions AS
WITH ranked_attempts AS (
    SELECT
        a.user_id,
        a.item_id,
        a.pct,
        a.created_at,
        ROW_NUMBER() OVER (
            PARTITION BY a.user_id, a.item_id
            ORDER BY a.created_at DESC
        ) AS rn
    FROM assessments.ap2_attempts a
)
SELECT
    last_a.user_id,
    last_a.item_id,
    i.topic_id,
    t.name_de       AS topic_name,
    t.slug          AS topic_slug,
    i.prompt        AS item_prompt,
    i.item_type     AS item_type,
    last_a.pct      AS last_pct,
    prev_a.pct      AS prev_pct,
    (prev_a.pct - last_a.pct) AS regression_size,
    last_a.created_at AS last_attempt_at,
    prev_a.created_at AS prev_attempt_at
FROM ranked_attempts last_a
JOIN ranked_attempts prev_a
    ON  prev_a.user_id = last_a.user_id
    AND prev_a.item_id = last_a.item_id
    AND prev_a.rn = 2
JOIN assessments.ap2_learning_items i ON i.item_id = last_a.item_id
JOIN assessments.ap2_topics         t ON t.topic_id = i.topic_id
WHERE last_a.rn = 1
  AND last_a.pct < prev_a.pct - 5;     -- mind. 5%-Punkte schlechter

COMMENT ON VIEW assessments.ap2_recent_regressions IS
    'Items wo der letzte Versuch schlechter war als der vorletzte (>=5%-Punkte). '
    'Treibt die "Mini-Schwächen"-Sektion im Dashboard.';
