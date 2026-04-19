-- ============================================================================
-- Migration: 137_ap2_modules_telegram.sql
-- Description: Modul-System mit strenger Mastery-Logik + Telegram-Bot-
--              Verknüpfung. Module sind übergeordnete Lerneinheiten,
--              jedes mit Lehrblock + 5-7 Aufgaben aus einem Pool.
--              Mastery: 3× hintereinander ≥80% + Same-Day-Recall ≥80%.
--              Spot-Checks: Tag 1+4h, 2, 4, 7, 12, 18 (kurz wegen Zeitnot).
--
--              Telegram-Felder in core.users: chat_id (für Pings) +
--              link_code (einmaliger 6-stelliger Code für Account-
--              Verknüpfung via /start CODE im Bot).
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-04-19
-- ============================================================================

-- ============================================================================
-- Teil 1: Telegram-Felder in core.users
-- ============================================================================

ALTER TABLE core.users
    ADD COLUMN IF NOT EXISTS telegram_chat_id BIGINT,
    ADD COLUMN IF NOT EXISTS telegram_link_code VARCHAR(8),
    ADD COLUMN IF NOT EXISTS telegram_link_expires_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS telegram_linked_at TIMESTAMPTZ;

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_telegram_chat_id
    ON core.users (telegram_chat_id)
    WHERE telegram_chat_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_users_telegram_link_code
    ON core.users (telegram_link_code)
    WHERE telegram_link_code IS NOT NULL;

COMMENT ON COLUMN core.users.telegram_chat_id IS
'Telegram chat_id für Bot-Pings. NULL wenn nicht verknüpft.';
COMMENT ON COLUMN core.users.telegram_link_code IS
'Einmaliger Code, mit dem User /start CODE im Bot sendet zur Verknüpfung.';

-- ============================================================================
-- Teil 2: ap2_modules — die Lehreinheiten
-- ============================================================================

CREATE TABLE IF NOT EXISTS assessments.ap2_modules (
    module_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(60) NOT NULL UNIQUE,
    name_de VARCHAR(120) NOT NULL,
    name_en VARCHAR(120),
    description TEXT,
    -- Lehrblock-Inhalt (Markdown), wird als allererste "Aufgabe" im Modul gezeigt
    theory_markdown TEXT,
    -- Geschätzte Lerndauer in Minuten (für UI-Anzeige)
    estimated_min INTEGER NOT NULL DEFAULT 12,
    difficulty INTEGER NOT NULL DEFAULT 3 CHECK (difficulty >= 1 AND difficulty <= 5),
    sort_order INTEGER NOT NULL DEFAULT 0,
    -- Welche Module müssen vorher mastered sein? (Liste von slugs)
    prerequisite_slugs JSONB DEFAULT '[]'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ap2_modules_active_sort
    ON assessments.ap2_modules (sort_order)
    WHERE is_active = TRUE;

COMMENT ON TABLE assessments.ap2_modules IS
'Lehrmodule (z.B. "IPv6-Konfiguration", "Organigramm lesen"). Jedes Modul hat einen Lehrblock + Pool von Aufgaben über ap2_module_items.';

-- ============================================================================
-- Teil 3: ap2_module_items — Verknüpfung Module ↔ Aufgaben (Pool)
-- ============================================================================

CREATE TABLE IF NOT EXISTS assessments.ap2_module_items (
    module_id UUID NOT NULL REFERENCES assessments.ap2_modules(module_id) ON DELETE CASCADE,
    item_id UUID NOT NULL REFERENCES assessments.ap2_learning_items(item_id) ON DELETE CASCADE,
    -- Schwierigkeitskategorie innerhalb des Moduls (1=Einstieg, 2=Standard, 3=fortgeschritten)
    pool_tier INTEGER NOT NULL DEFAULT 2 CHECK (pool_tier >= 1 AND pool_tier <= 3),
    -- Wofür wird das Item genutzt? 'mastery'=in Mastery-Loop, 'spotcheck'=in Spot-Checks,
    -- 'both'=in beiden
    use_in VARCHAR(16) NOT NULL DEFAULT 'both' CHECK (use_in IN ('mastery', 'spotcheck', 'both')),
    sort_order INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (module_id, item_id)
);

CREATE INDEX IF NOT EXISTS idx_ap2_module_items_module_tier
    ON assessments.ap2_module_items (module_id, pool_tier);

-- ============================================================================
-- Teil 4: ap2_module_progress — User-spezifischer Fortschritt
-- ============================================================================

CREATE TABLE IF NOT EXISTS assessments.ap2_module_progress (
    progress_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    module_id UUID NOT NULL REFERENCES assessments.ap2_modules(module_id) ON DELETE CASCADE,

    -- Status-Maschine
    status VARCHAR(16) NOT NULL DEFAULT 'locked'
        CHECK (status IN ('locked', 'available', 'learning', 'pending_recall', 'mastered', 'review_failed')),

    -- Mastery-Logik
    -- Streak: aktuelle Anzahl direkt aufeinanderfolgender ≥80%-Versuche
    streak_count INTEGER NOT NULL DEFAULT 0,
    -- Anzahl Aufgaben dieses Mastery-Versuchs (Reset bei <80%)
    total_attempts INTEGER NOT NULL DEFAULT 0,
    -- Anzahl bestandener Aufgaben (≥80%) seit Modul-Start
    passed_attempts INTEGER NOT NULL DEFAULT 0,
    -- Cooldown bis User wieder versuchen darf (nach 3× Scheitern)
    cooldown_until TIMESTAMPTZ,

    -- Same-Day-Recall (nach 3 Streak-Erfolgen)
    -- Wird gesetzt wenn 3× ≥80% erreicht — Recall ist 4h später fällig
    same_day_recall_due_at TIMESTAMPTZ,
    same_day_recall_passed BOOLEAN,

    -- Mastery erreicht
    mastered_at TIMESTAMPTZ,

    -- Spot-Check-Schedule (nach Mastery)
    -- Welche Stufe (0=Tag 2, 1=Tag 4, 2=Tag 7, 3=Tag 12, 4=Tag 18, 5+=2x letzte Stufe)
    spotcheck_stage INTEGER NOT NULL DEFAULT 0,
    next_spotcheck_at TIMESTAMPTZ,
    last_spotcheck_at TIMESTAMPTZ,
    last_spotcheck_score NUMERIC(5,2),

    -- Welche Items wurden in dieser Session schon verwendet (damit System nicht 2× das gleiche zieht)
    used_item_ids JSONB DEFAULT '[]'::jsonb,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (user_id, module_id)
);

CREATE INDEX IF NOT EXISTS idx_ap2_module_progress_user_status
    ON assessments.ap2_module_progress (user_id, status);

CREATE INDEX IF NOT EXISTS idx_ap2_module_progress_due_spotchecks
    ON assessments.ap2_module_progress (next_spotcheck_at)
    WHERE status = 'mastered' AND next_spotcheck_at IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_ap2_module_progress_due_recalls
    ON assessments.ap2_module_progress (same_day_recall_due_at)
    WHERE status = 'pending_recall' AND same_day_recall_due_at IS NOT NULL;

COMMENT ON TABLE assessments.ap2_module_progress IS
'Pro User pro Modul: Status, Mastery-Streak, Spot-Check-Schedule. Strenge Logik: 3× ≥80% in Folge + Same-Day-Recall ≥80% = mastered.';

-- ============================================================================
-- Teil 5: ap2_module_attempt_log — Audit-Trail jeder Mastery/Spot-Check-Antwort
-- ============================================================================

CREATE TABLE IF NOT EXISTS assessments.ap2_module_attempt_log (
    attempt_log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    module_id UUID NOT NULL REFERENCES assessments.ap2_modules(module_id) ON DELETE CASCADE,
    item_id UUID NOT NULL REFERENCES assessments.ap2_learning_items(item_id) ON DELETE CASCADE,

    -- Phase: 'mastery'=während Mastery-Loop, 'recall'=Same-Day-Recall, 'spotcheck'=späterer Spot-Check
    attempt_phase VARCHAR(16) NOT NULL CHECK (attempt_phase IN ('mastery', 'recall', 'spotcheck')),

    -- Quelle: 'webapp' oder 'telegram'
    source VARCHAR(16) NOT NULL DEFAULT 'webapp' CHECK (source IN ('webapp', 'telegram')),

    user_answer TEXT NOT NULL,
    score_pct NUMERIC(5,2) NOT NULL,
    passed BOOLEAN NOT NULL,
    feedback JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ap2_attempt_log_user_module
    ON assessments.ap2_module_attempt_log (user_id, module_id, created_at DESC);

-- ============================================================================
-- Teil 6: Trigger für updated_at
-- ============================================================================

CREATE OR REPLACE FUNCTION assessments.update_modules_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_ap2_modules_updated ON assessments.ap2_modules;
CREATE TRIGGER trg_ap2_modules_updated
    BEFORE UPDATE ON assessments.ap2_modules
    FOR EACH ROW EXECUTE FUNCTION assessments.update_modules_timestamp();

DROP TRIGGER IF EXISTS trg_ap2_module_progress_updated ON assessments.ap2_module_progress;
CREATE TRIGGER trg_ap2_module_progress_updated
    BEFORE UPDATE ON assessments.ap2_module_progress
    FOR EACH ROW EXECUTE FUNCTION assessments.update_modules_timestamp();

COMMIT;
