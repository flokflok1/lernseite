-- ============================================================================
-- Migration: 120_ap2_trainer.sql
-- Description: AP2 Trainer (FISI FA 235 Baden-Württemberg) — Active Recall,
--              SM-2 Spaced Repetition, beschriftbare Anlagen, IHK-Stil.
--              7 neue Tabellen im bestehenden `assessments` Schema.
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-04-18
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. TOPICS — 25+ Kernthemen mit Priorität + Bereich (PB2/PB3/WISO)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS assessments.ap2_topics (
    topic_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(80) NOT NULL UNIQUE,
    name_de VARCHAR(200) NOT NULL,
    name_en VARCHAR(200),
    bereich VARCHAR(10) NOT NULL CHECK (bereich IN ('PB2', 'PB3', 'WISO', 'both')),
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('sehr-hoch', 'hoch', 'mittel', 'niedrig')),
    expected_points INT NOT NULL DEFAULT 0,
    exam_count INT NOT NULL DEFAULT 0,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ap2_topics_bereich ON assessments.ap2_topics (bereich);
CREATE INDEX IF NOT EXISTS idx_ap2_topics_priority ON assessments.ap2_topics (priority);

COMMENT ON TABLE assessments.ap2_topics IS
    'AP2 Kernthemen für FA 235 Baden-Württemberg. Priorität basiert auf Häufigkeit in Prüfungen ab 2022.';

-- ---------------------------------------------------------------------------
-- 2. ANLAGEN — Referenz-Material mit Hotspots (beschriftbar)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS assessments.ap2_anlagen (
    anlage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(120) NOT NULL UNIQUE,
    title VARCHAR(300) NOT NULL,
    anlage_type VARCHAR(40) NOT NULL CHECK (anlage_type IN (
        'network-topology', 'datasheet', 'table', 'er-diagram',
        'rack-layout', 'process-diagram', 'epk-diagram',
        'state-diagram', 'sequence-diagram', 'image'
    )),
    source_exam VARCHAR(80),         -- z.B. 'S2024-PB2', 'AP1-2026-Sommer'
    anlage_number INT,               -- "Anlage 2" → 2
    image_url TEXT,                  -- /static/ap2/anlagen/{slug}.png
    image_width INT,
    image_height INT,
    svg_markup TEXT,                 -- Alternative zu image_url: reines SVG
    hotspots JSONB NOT NULL DEFAULT '[]'::jsonb,  -- [{id, x, y, type, correctAnswers, points}]
    description TEXT,
    footnote TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ap2_anlagen_type ON assessments.ap2_anlagen (anlage_type);
CREATE INDEX IF NOT EXISTS idx_ap2_anlagen_source ON assessments.ap2_anlagen (source_exam);

COMMENT ON TABLE assessments.ap2_anlagen IS
    'Beschriftbare Prüfungs-Anlagen (Netzpläne, ER-Modelle, Datenblätter). Hotspots als JSONB für Flex.';
COMMENT ON COLUMN assessments.ap2_anlagen.hotspots IS
    'Array von Hotspot-Objekten: {id, x, y, width, height, type, correctAnswers[], tolerance, points, hint}';

-- ---------------------------------------------------------------------------
-- 3. LEARNING ITEMS — Atome des Active-Recall-Flows (blurt / cued / application)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS assessments.ap2_learning_items (
    item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_id UUID NOT NULL REFERENCES assessments.ap2_topics(topic_id) ON DELETE CASCADE,
    item_type VARCHAR(20) NOT NULL CHECK (item_type IN ('blurt', 'cued', 'application')),

    prompt TEXT NOT NULL,
    expected_answer_structure JSONB,  -- Checkliste für KI-Bewertung (Blurt)
    model_answer TEXT NOT NULL,
    grading_criteria JSONB,           -- [{criterion, weight, description}]
    points NUMERIC(5,2) NOT NULL DEFAULT 1.0,

    source_exam VARCHAR(80),          -- z.B. 'S2024-PB2-1.1' oder 'ki-generated'
    anlage_id UUID REFERENCES assessments.ap2_anlagen(anlage_id) ON DELETE SET NULL,

    difficulty INT CHECK (difficulty BETWEEN 1 AND 5),
    estimated_time_sec INT,           -- ~300 für Blurt, ~120 für Cued, ~600 für Application

    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ap2_items_topic ON assessments.ap2_learning_items (topic_id);
CREATE INDEX IF NOT EXISTS idx_ap2_items_topic_type ON assessments.ap2_learning_items (topic_id, item_type);
CREATE INDEX IF NOT EXISTS idx_ap2_items_active ON assessments.ap2_learning_items (is_active)
    WHERE is_active = TRUE;

COMMENT ON TABLE assessments.ap2_learning_items IS
    'Lern-Atome: Blurting-Prompt, Karteikarten-Frage, oder Prüfungsaufgabe. Pro Topic mehrere pro Type.';

-- ---------------------------------------------------------------------------
-- 4. ATTEMPTS — Jeder User-Versuch eines Learning-Items
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS assessments.ap2_attempts (
    attempt_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    item_id UUID NOT NULL REFERENCES assessments.ap2_learning_items(item_id) ON DELETE CASCADE,

    phase VARCHAR(20) NOT NULL CHECK (phase IN ('blurt', 'cued', 'application', 'review')),

    answer_text TEXT,
    answer_hotspots JSONB,            -- { "hotspot_id": "user_value" }

    pct INT CHECK (pct BETWEEN 0 AND 100),
    points_earned NUMERIC(5,2),
    points_total NUMERIC(5,2),

    feedback TEXT,
    feedback_structured JSONB,        -- { missing: [], correct: [], partial: [] }
    ai_model VARCHAR(80),

    time_spent_sec INT,
    sm2_quality INT CHECK (sm2_quality BETWEEN 0 AND 5),  -- Self-rating for SM-2

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ap2_attempts_user_item
    ON assessments.ap2_attempts (user_id, item_id);
CREATE INDEX IF NOT EXISTS idx_ap2_attempts_user_created
    ON assessments.ap2_attempts (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ap2_attempts_item
    ON assessments.ap2_attempts (item_id);

COMMENT ON TABLE assessments.ap2_attempts IS
    'Jeder Versuch eines Items. Treibt Mastery-Berechnung und SM-2-Scheduling.';

-- ---------------------------------------------------------------------------
-- 5. REVIEW SCHEDULE — SM-2 State pro User+Item
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS assessments.ap2_review_schedule (
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    item_id UUID NOT NULL REFERENCES assessments.ap2_learning_items(item_id) ON DELETE CASCADE,

    -- SM-2 State
    ease_factor NUMERIC(4,2) NOT NULL DEFAULT 2.5,
    interval_days INT NOT NULL DEFAULT 1,
    repetitions INT NOT NULL DEFAULT 0,
    next_review_at TIMESTAMPTZ NOT NULL,
    last_quality INT CHECK (last_quality BETWEEN 0 AND 5),
    last_reviewed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (user_id, item_id)
);

CREATE INDEX IF NOT EXISTS idx_ap2_schedule_user_due
    ON assessments.ap2_review_schedule (user_id, next_review_at)
    WHERE next_review_at IS NOT NULL;

COMMENT ON TABLE assessments.ap2_review_schedule IS
    'SM-2 Spaced Repetition: next_review_at steuert Review-Queue.';

-- ---------------------------------------------------------------------------
-- 6. TOPIC MASTERY — Aggregat pro User+Topic (für Dashboard + Prognose)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS assessments.ap2_topic_mastery (
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    topic_id UUID NOT NULL REFERENCES assessments.ap2_topics(topic_id) ON DELETE CASCADE,

    mastery_score NUMERIC(5,2) NOT NULL DEFAULT 0,    -- 0-100, EMA
    attempts_count INT NOT NULL DEFAULT 0,
    correct_count INT NOT NULL DEFAULT 0,
    total_points_earned NUMERIC(8,2) NOT NULL DEFAULT 0,
    total_points_possible NUMERIC(8,2) NOT NULL DEFAULT 0,

    last_attempt_at TIMESTAMPTZ,
    last_review_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (user_id, topic_id)
);

CREATE INDEX IF NOT EXISTS idx_ap2_mastery_user
    ON assessments.ap2_topic_mastery (user_id);

COMMENT ON TABLE assessments.ap2_topic_mastery IS
    'Aggregierte Mastery pro Thema. Basis für Prüfungs-Prognose + Schwächen-Analyse.';

-- ---------------------------------------------------------------------------
-- 7. CHEATSHEETS — User-generiertes Thema-Cheatsheet (Markdown)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS assessments.ap2_cheatsheets (
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    topic_id UUID NOT NULL REFERENCES assessments.ap2_topics(topic_id) ON DELETE CASCADE,

    markdown_content TEXT NOT NULL DEFAULT '',
    word_count INT NOT NULL DEFAULT 0,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (user_id, topic_id)
);

COMMENT ON TABLE assessments.ap2_cheatsheets IS
    'Vom User geschriebene Kurz-Zusammenfassung pro Thema (Markdown). Generation Effect.';

-- ---------------------------------------------------------------------------
-- 8. STUDY SESSIONS — Optional: Tracking einer zusammenhängenden Lerneinheit
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS assessments.ap2_study_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    topic_id UUID REFERENCES assessments.ap2_topics(topic_id) ON DELETE SET NULL,

    session_type VARCHAR(30) NOT NULL CHECK (session_type IN (
        'topic_study',      -- 3-Phasen-Flow zu einem Thema
        'review_queue',     -- SM-2 Queue
        'exam_simulation',  -- 90-Min Prüfung
        'mixed_practice'    -- Interleaving
    )),

    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    duration_sec INT,

    items_attempted INT NOT NULL DEFAULT 0,
    items_correct INT NOT NULL DEFAULT 0,
    points_earned NUMERIC(6,2) NOT NULL DEFAULT 0,
    points_possible NUMERIC(6,2) NOT NULL DEFAULT 0,

    completed BOOLEAN NOT NULL DEFAULT FALSE,
    metadata JSONB                     -- z.B. { phases_done: ['blurt', 'cued'] }
);

CREATE INDEX IF NOT EXISTS idx_ap2_sessions_user_started
    ON assessments.ap2_study_sessions (user_id, started_at DESC);

COMMENT ON TABLE assessments.ap2_study_sessions IS
    'Zusammenhängende Lerneinheit. Aggregiert Attempts für History-Ansicht.';

-- ---------------------------------------------------------------------------
-- 9. TRIGGER — updated_at automatisch setzen
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION assessments.ap2_touch_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS ap2_anlagen_updated_at ON assessments.ap2_anlagen;
CREATE TRIGGER ap2_anlagen_updated_at
    BEFORE UPDATE ON assessments.ap2_anlagen
    FOR EACH ROW EXECUTE FUNCTION assessments.ap2_touch_updated_at();

DROP TRIGGER IF EXISTS ap2_items_updated_at ON assessments.ap2_learning_items;
CREATE TRIGGER ap2_items_updated_at
    BEFORE UPDATE ON assessments.ap2_learning_items
    FOR EACH ROW EXECUTE FUNCTION assessments.ap2_touch_updated_at();

DROP TRIGGER IF EXISTS ap2_schedule_updated_at ON assessments.ap2_review_schedule;
CREATE TRIGGER ap2_schedule_updated_at
    BEFORE UPDATE ON assessments.ap2_review_schedule
    FOR EACH ROW EXECUTE FUNCTION assessments.ap2_touch_updated_at();

DROP TRIGGER IF EXISTS ap2_mastery_updated_at ON assessments.ap2_topic_mastery;
CREATE TRIGGER ap2_mastery_updated_at
    BEFORE UPDATE ON assessments.ap2_topic_mastery
    FOR EACH ROW EXECUTE FUNCTION assessments.ap2_touch_updated_at();

DROP TRIGGER IF EXISTS ap2_cheatsheets_updated_at ON assessments.ap2_cheatsheets;
CREATE TRIGGER ap2_cheatsheets_updated_at
    BEFORE UPDATE ON assessments.ap2_cheatsheets
    FOR EACH ROW EXECUTE FUNCTION assessments.ap2_touch_updated_at();

-- ---------------------------------------------------------------------------
-- 10. SEED — 25 Kernthemen (basierend auf Prüfungsanalyse S2022-S2024)
--     Punkte = Durchschnitt über die 5 analysierten Prüfungstermine.
-- ---------------------------------------------------------------------------

INSERT INTO assessments.ap2_topics (slug, name_de, name_en, bereich, priority, expected_points, exam_count, description) VALUES
    -- PB2 — Sehr hoch
    ('ipv4-subnetting',     'IPv4-Subnetting (VLSM, CIDR)',       'IPv4 Subnetting',                'PB2',  'sehr-hoch', 15, 10, 'CIDR-Notation, VLSM lückenlos, Netz/Broadcast/Hostrange'),
    ('vpn-verschluesselung','VPN + Verschlüsselung (sym/asym/hybrid)', 'VPN + Encryption',          'PB2',  'sehr-hoch', 12, 8,  'IPsec Tunnel/Transport, Authentizität/Integrität/Vertraulichkeit'),
    ('dmz-firewall',        'DMZ + Firewall-Konzepte',            'DMZ + Firewall',                 'both', 'sehr-hoch', 10, 7,  'Einstufiges vs. zweistufiges Konzept, Placement'),
    ('sql-queries',         'SQL (SELECT, JOIN, Subquery, UPDATE)','SQL Queries',                   'PB2',  'sehr-hoch', 15, 9,  'Komplexe Abfragen, CREATE TABLE, Normalisierung'),
    ('epk',                 'EPK — Ereignisgesteuerte Prozesskette','EPK Modeling',                 'both', 'sehr-hoch', 14, 9,  'Ereignis/Funktion/Konnektor XOR-UND-ODER, selbst erstellen'),
    -- PB2 — Hoch
    ('rechtsformen',        'Rechtsformen (EU vs. GmbH vs. UG)',  'Legal Forms',                    'PB2',  'hoch',       8, 4,  'Haftung, Gründung, Stammkapital, Handelsregister'),
    ('organigramm',         'Organigramm + Organisationsformen',  'Org Charts',                     'PB2',  'hoch',       8, 3,  'Stablinien/Matrix/Linien + Vor-/Nachteile'),
    ('vollmachten',         'Prokura (ppa.) vs. Handlungsvollmacht (i.V.)', 'Authorities',          'PB2',  'hoch',       6, 3,  'Umfang, Eintragung, Übertragbarkeit'),
    ('zuschlagskalkulation','Zuschlagskalkulation (MEK→VKP)',     'Cost Calculation',               'PB2',  'hoch',      12, 4,  'Material/Fertigung/Selbst/Netto/Brutto mit MwSt'),
    ('kaufvertrag',         'Kaufvertrag-Ablauf + Willenserklärung','Sales Contract',              'PB2',  'hoch',       4, 4,  'Anfrage/Angebot/Bestellung, 2 Willenserklärungen'),
    ('wlan',                'WLAN (AP-Auswahl, WPA3, 2,4/5GHz)',  'WLAN Standards',                 'PB2',  'hoch',      10, 5,  'Störquellen, 802.11ax/be (Wi-Fi 6/7), PoE'),
    ('nutzwertanalyse',     'Nutzwertanalyse (Cloud vs. On-Prem)','Utility Analysis',               'PB2',  'hoch',      10, 3,  'Gewichtung × Bewertung, Kriterien-Matrix'),
    ('projektmanagement',   'Projektmanagement (Wasserfall/Scrum)','Project Management',            'both', 'hoch',      10, 9,  'Phasen, agile Methoden, Risikomanagement, TCO/ROI'),
    ('iot-cps',             'IoT/CPS + Sensoren + Edge Computing','IoT/CPS',                        'PB2',  'hoch',      12, 3,  'Aktoren, LP-WAN, MQTT, Edge vs. Cloud'),
    ('vlan',                'VLAN (802.1Q, Trunk, Voice/Mgmt/Default)','VLAN',                     'both', 'hoch',      10, 6,  'Tagged/untagged, max. 4094, Trunk'),
    -- PB3 — Sehr hoch
    ('ipv6-subnetting',     'IPv6 (Kürzung, EUI-64, Dual-Stack)', 'IPv6 Subnetting',                'PB3',  'sehr-hoch',  8, 7,  'Kurzform, Link-local vs. Global, ip-address-Output lesen'),
    ('er-modell',           'ER-Modell + Relationales Modell + Normalisierung','ER Model',          'PB3',  'sehr-hoch', 12, 7,  '1-3 NF, Anomalien, n:m-Auflösung, FK/PK'),
    ('netzwerkanalyse',     '3-Layer-Architektur (Core/Distribution/Access)','Network Analysis',    'PB3',  'sehr-hoch', 14, 3,  'Protokoll-Zuordnung: STP, NAT/PAT, OSPF, FHRP, DHCP'),
    ('osi-troubleshooting', 'OSI-Bottom-Up-Troubleshooting',      'OSI Troubleshooting',            'PB3',  'sehr-hoch', 10, 2,  'Je Schicht ein Fehler + Testmethode — Dozent-Schwerpunkt'),
    ('usv',                 'USV — Überbrückungszeit, VA, Leistungsfaktor','UPS',                   'PB3',  'sehr-hoch',  8, 1,  'VFD/VI/VFI, Graph-Ablesung, Berechnung — Dozent-Skript'),
    ('code-analyse',        'Code analysieren (Struktogramm/PAP/Pseudocode)','Code Analysis',       'PB3',  'sehr-hoch', 18, 3,  'Trend: W2022 8P → S2024 20P — stark steigend'),
    -- PB3 — Hoch / Mittel
    ('schutzbedarf-bsi',    'Schutzbedarfsanalyse BSI + Risikomatrix','BSI Risk Analysis',          'PB3',  'hoch',      15, 1,  'Hoch/normal/sehr hoch, CIA-Triade, Eintritt × Schaden'),
    ('virtualisierung',     'Virtualisierung (Hypervisor Typ 1/2)','Virtualization',                'PB3',  'hoch',       8, 1,  'VM vs. Container, Vor-/Nachteile'),
    ('snmp-monitoring',     'SNMP-Monitoring (v2/v3 + Trap) + SSH/HTTPS','SNMP',                    'PB3',  'hoch',       8, 3,  'Fernverwaltungs-Sicherheit, Community-String vs. User'),
    ('mqtt',                'MQTT (Broker, Topic, Publish/Subscribe)','MQTT',                       'PB3',  'mittel',     6, 2,  'Für IoT, QoS-Levels, Retain'),
    -- WISO (eigener Track)
    ('wiso-sozialversicherung','Sozialversicherung (KV/PV/RV/AV/UV)','Social Insurance',           'WISO', 'sehr-hoch', 10, 5,  'Beitragssätze, Versicherungsfälle'),
    ('wiso-tarif',          'Tarifverhandlungen + Betriebsrat',   'Collective Bargaining',         'WISO', 'hoch',       8, 4,  'Tarifautonomie, Mitbestimmung, BetrVG'),
    ('wiso-rechtsgeschaeft','Rechtsgeschäfte + Kaufvertragsstörungen','Legal Transactions',        'WISO', 'hoch',       8, 4,  'Mangelarten, Gewährleistung, Verzug')
ON CONFLICT (slug) DO NOTHING;
