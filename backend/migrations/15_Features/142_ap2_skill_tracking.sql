-- ============================================================================
-- Migration: 142_ap2_skill_tracking.sql
-- Description: Stützrad-Modus + Skill-Tracking pro User+Item.
--              User stellt Ziel selbst ein (3-7x), Recovery-Logik erhöht
--              das Ziel bei Failures. Stützrad = Musterlösung lesen, keine
--              Streak-Änderung. Modul-Mastery basiert auf bewältigten Items.
--
--              2 neue Tabellen:
--              - ap2_user_learning_prefs  (globale Einstellungen pro User)
--              - ap2_module_item_skill    (pro User pro Item: Fortschritt)
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-04-19
-- ============================================================================

-- ============================================================================
-- Teil 1: User-Lern-Präferenzen (globale Einstellungen)
-- ============================================================================

CREATE TABLE IF NOT EXISTS assessments.ap2_user_learning_prefs (
    user_id UUID PRIMARY KEY REFERENCES core.users(user_id) ON DELETE CASCADE,

    -- Basis-Ziel: wie viele richtige Antworten in Folge (Stützrad aus) bis Item sitzt
    base_target INTEGER NOT NULL DEFAULT 3 CHECK (base_target BETWEEN 1 AND 10),

    -- Max-Ziel im Recovery: Cap nach Fails
    max_target INTEGER NOT NULL DEFAULT 10 CHECK (max_target BETWEEN 2 AND 20),

    -- Recovery-Verhalten bei Fehler
    recovery_mode VARCHAR(16) NOT NULL DEFAULT 'plus_two'
        CHECK (recovery_mode IN ('plus_one', 'plus_two', 'multiply_1_5')),

    -- Default-Modus für Stützrad beim Öffnen eines Items
    stuetzrad_default VARCHAR(16) NOT NULL DEFAULT 'per_item'
        CHECK (stuetzrad_default IN ('off', 'per_item', 'first_two_on')),

    -- Mastery-Strenge für Modul
    mastery_strictness VARCHAR(16) NOT NULL DEFAULT 'standard'
        CHECK (mastery_strictness IN ('express', 'standard', 'strict')),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE assessments.ap2_user_learning_prefs IS
'Pro User konfigurierte Lern-Einstellungen für das Modul-/Stützrad-System.';

-- ============================================================================
-- Teil 2: Pro User pro Item — Fortschritt
-- ============================================================================

CREATE TABLE IF NOT EXISTS assessments.ap2_module_item_skill (
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    item_id UUID NOT NULL REFERENCES assessments.ap2_learning_items(item_id) ON DELETE CASCADE,

    -- Wie viele Stützrad-AUS-Erfolge in Folge
    kopf_serie_count INTEGER NOT NULL DEFAULT 0,

    -- Wie viele Fehler insgesamt für dieses Item (nur Stützrad AUS)
    fail_count INTEGER NOT NULL DEFAULT 0,

    -- Effektives Ziel = base_target + (fail_count × recovery_step), gecapped durch max_target
    effective_target INTEGER NOT NULL DEFAULT 3,

    -- Gesamt-Versuche (für Statistik)
    total_attempts INTEGER NOT NULL DEFAULT 0,

    -- Wie oft Stützrad benutzt (nur Zähler, kein Streak)
    stuetzrad_uses INTEGER NOT NULL DEFAULT 0,

    -- Status
    is_mastered BOOLEAN NOT NULL DEFAULT FALSE,
    mastered_at TIMESTAMPTZ,

    -- "Ich geb auf heute" — Item bleibt bis TS ausgeblendet
    snoozed_until TIMESTAMPTZ,

    last_attempt_at TIMESTAMPTZ,
    last_score_pct NUMERIC(5,2),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    PRIMARY KEY (user_id, item_id)
);

CREATE INDEX IF NOT EXISTS idx_ap2_skill_user_mastered
    ON assessments.ap2_module_item_skill (user_id, is_mastered);

CREATE INDEX IF NOT EXISTS idx_ap2_skill_user_snoozed
    ON assessments.ap2_module_item_skill (user_id, snoozed_until)
    WHERE snoozed_until IS NOT NULL;

COMMENT ON TABLE assessments.ap2_module_item_skill IS
'Pro User pro Item: Kopf-Serie, Fails, effektives Ziel, Stützrad-Zähler,
Mastery-Status. Grundlage für "Item sitzt"-Gate.';

-- ============================================================================
-- Teil 3: Trigger für updated_at
-- ============================================================================

CREATE OR REPLACE FUNCTION assessments.update_skill_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_ap2_prefs_updated ON assessments.ap2_user_learning_prefs;
CREATE TRIGGER trg_ap2_prefs_updated
    BEFORE UPDATE ON assessments.ap2_user_learning_prefs
    FOR EACH ROW EXECUTE FUNCTION assessments.update_skill_timestamp();

DROP TRIGGER IF EXISTS trg_ap2_skill_updated ON assessments.ap2_module_item_skill;
CREATE TRIGGER trg_ap2_skill_updated
    BEFORE UPDATE ON assessments.ap2_module_item_skill
    FOR EACH ROW EXECUTE FUNCTION assessments.update_skill_timestamp();

COMMIT;
