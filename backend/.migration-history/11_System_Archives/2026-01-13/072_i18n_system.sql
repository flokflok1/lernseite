-- ============================================================================
-- Migration 072: Vollständiges i18n-System (Website + Kurse)
-- ============================================================================
--
-- Flexibles Internationalisierungs-System mit:
-- 1. Namespace-basierte Organisation (auth, dashboard, courses, etc.)
-- 2. Community-Übersetzungsvorschläge mit Voting
-- 3. On-Demand Generierung für neue Sprachen
-- 4. Primär-Sprachen: DE, PL, EN (in dieser Reihenfolge)
--
-- ============================================================================

-- ============================================================================
-- 1. i18n_namespaces - Gruppierung der Übersetzungen
-- ============================================================================

CREATE TABLE IF NOT EXISTS translations.i18n_namespaces (
    namespace_id SERIAL PRIMARY KEY,
    namespace_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_i18n_namespaces_code ON translations.i18n_namespaces (namespace_code);
CREATE INDEX IF NOT EXISTS idx_i18n_namespaces_active ON translations.i18n_namespaces (is_active) WHERE is_active = TRUE;

COMMENT ON TABLE translations.i18n_namespaces IS
'Namespaces für i18n-Keys (common, auth, dashboard, admin, courses, errors, emails, etc.)';

-- ============================================================================
-- 1b. Standard Namespaces
-- ============================================================================

INSERT INTO translations.i18n_namespaces (namespace_code, name, description, icon, sort_order)
VALUES
    ('common', 'Allgemein', 'Allgemeine UI-Elemente (Buttons, Labels, etc.)', '🔤', 10),
    ('auth', 'Authentifizierung', 'Login, Registrierung, Passwort-Reset', '🔐', 20),
    ('navigation', 'Navigation', 'Menüs, Breadcrumbs, Links', '🧭', 30),
    ('dashboard', 'Dashboard', 'Dashboard-Widgets und Übersichten', '📊', 40),
    ('courses', 'Kurse', 'Kurs-Übersicht, Kurs-Details, Lektionen', '📚', 50),
    ('player', 'Lern-Player', 'Lernmethoden-Player, Quiz, Übungen', '▶️', 60),
    ('editor', 'Editor', 'Kurs-Editor, Content-Erstellung', '✏️', 70),
    ('admin', 'Administration', 'Admin-Panel, Einstellungen', '⚙️', 80),
    ('ai_studio', 'KI-Studio', 'KI-Authoring, Chat, Generierung', '🤖', 90),
    ('profile', 'Profil', 'Benutzer-Profil, Einstellungen', '👤', 100),
    ('org', 'Organisation', 'Schul-/Unternehmens-Verwaltung', '🏢', 110),
    ('notifications', 'Benachrichtigungen', 'System-Benachrichtigungen, Alerts', '🔔', 120),
    ('emails', 'E-Mails', 'E-Mail-Templates', '📧', 130),
    ('errors', 'Fehler', 'Fehlermeldungen, Validierung', '⚠️', 140),
    ('tooltips', 'Tooltips', 'Hilfetexte, Erklärungen', '💡', 150),
    ('dates', 'Datum/Zeit', 'Datumsformate, Zeitangaben', '📅', 160),
    ('numbers', 'Zahlen', 'Zahlenformate, Währung', '🔢', 170)
ON CONFLICT (namespace_code) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    icon = EXCLUDED.icon,
    sort_order = EXCLUDED.sort_order,
    updated_at = NOW();

-- ============================================================================
-- 2. i18n_keys - Übersetzungs-Schlüssel
-- ============================================================================

CREATE TABLE IF NOT EXISTS translations.i18n_keys (
    key_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace_id INTEGER NOT NULL REFERENCES translations.i18n_namespaces(namespace_id) ON DELETE CASCADE,

    -- Key-Pfad (z.B. "button.save", "error.required")
    key_path VARCHAR(255) NOT NULL,

    -- Kontext für Übersetzer
    context TEXT,

    -- Screenshot/Beispiel-URL wo der Text erscheint
    screenshot_url VARCHAR(500),

    -- Platzhalter die im Text verwendet werden
    -- z.B. ["username", "count", "date"]
    placeholders JSONB DEFAULT '[]',

    -- Hat Plural-Formen?
    is_plural BOOLEAN DEFAULT FALSE,

    -- Maximale Textlänge (für UI-Constraints)
    max_length INTEGER,

    -- Meta
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES core.users(user_id),

    UNIQUE (namespace_id, key_path)
);

CREATE INDEX IF NOT EXISTS idx_i18n_keys_namespace ON translations.i18n_keys (namespace_id);
CREATE INDEX IF NOT EXISTS idx_i18n_keys_path ON translations.i18n_keys (key_path);
CREATE INDEX IF NOT EXISTS idx_i18n_keys_plural ON translations.i18n_keys (is_plural) WHERE is_plural = TRUE;

COMMENT ON TABLE translations.i18n_keys IS
'Alle übersetzbaren Text-Schlüssel mit Kontext für Übersetzer';

-- ============================================================================
-- 3. i18n_translations - Die eigentlichen Übersetzungen
-- ============================================================================

CREATE TABLE IF NOT EXISTS translations.i18n_translations (
    translation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key_id UUID NOT NULL REFERENCES translations.i18n_keys(key_id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL REFERENCES translations.supported_languages(language_code),

    -- Übersetzter Text
    value TEXT NOT NULL,

    -- Plural-Formen (für is_plural=true Keys)
    -- {"zero": "Keine Kurse", "one": "1 Kurs", "few": "...", "many": "...", "other": "{n} Kurse"}
    plural_forms JSONB,

    -- Status der Übersetzung
    status VARCHAR(20) NOT NULL DEFAULT 'active',

    -- Quelle: manual, deepl, google, community, ai
    source VARCHAR(50) NOT NULL DEFAULT 'manual',

    -- Qualitätssicherung
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by UUID REFERENCES core.users(user_id),
    verified_at TIMESTAMPTZ,

    -- Wenn maschinell übersetzt: Confidence
    machine_confidence DECIMAL(3,2),

    -- Versioning
    version INTEGER DEFAULT 1,

    -- Meta
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES core.users(user_id),

    UNIQUE (key_id, language_code),
    CONSTRAINT chk_translation_status CHECK (status IN ('draft', 'active', 'needs_review', 'outdated')),
    CONSTRAINT chk_translation_source CHECK (source IN ('manual', 'deepl', 'google', 'community', 'ai', 'import'))
);

CREATE INDEX IF NOT EXISTS idx_i18n_translations_key ON translations.i18n_translations (key_id);
CREATE INDEX IF NOT EXISTS idx_i18n_translations_lang ON translations.i18n_translations (language_code);
CREATE INDEX IF NOT EXISTS idx_i18n_translations_status ON translations.i18n_translations (status);
CREATE INDEX IF NOT EXISTS idx_i18n_translations_unverified ON translations.i18n_translations (is_verified) WHERE is_verified = FALSE;

COMMENT ON TABLE translations.i18n_translations IS
'Übersetzungen für alle Keys in allen Sprachen';

-- ============================================================================
-- 4. i18n_suggestions - Community-Übersetzungsvorschläge
-- ============================================================================

CREATE TABLE IF NOT EXISTS translations.i18n_suggestions (
    suggestion_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    translation_id UUID REFERENCES translations.i18n_translations(translation_id) ON DELETE CASCADE,

    -- Alternativ: Direkter Bezug auf Key (wenn noch keine Übersetzung existiert)
    key_id UUID REFERENCES translations.i18n_keys(key_id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL REFERENCES translations.supported_languages(language_code),

    -- Vorgeschlagener Text
    suggested_value TEXT NOT NULL,

    -- Für Plural-Formen
    suggested_plural_forms JSONB,

    -- Begründung
    reason TEXT,

    -- Wer hat vorgeschlagen
    suggested_by UUID NOT NULL REFERENCES core.users(user_id),
    suggested_at TIMESTAMPTZ DEFAULT NOW(),

    -- Community-Voting
    votes_up INTEGER DEFAULT 0,
    votes_down INTEGER DEFAULT 0,
    vote_score INTEGER GENERATED ALWAYS AS (votes_up - votes_down) STORED,

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'pending',

    -- Review
    reviewed_by UUID REFERENCES core.users(user_id),
    reviewed_at TIMESTAMPTZ,
    review_comment TEXT,

    CONSTRAINT chk_suggestion_status CHECK (status IN ('pending', 'approved', 'rejected', 'duplicate')),
    CONSTRAINT chk_suggestion_ref CHECK (translation_id IS NOT NULL OR key_id IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_i18n_suggestions_translation ON translations.i18n_suggestions (translation_id);
CREATE INDEX IF NOT EXISTS idx_i18n_suggestions_key ON translations.i18n_suggestions (key_id);
CREATE INDEX IF NOT EXISTS idx_i18n_suggestions_status ON translations.i18n_suggestions (status);
CREATE INDEX IF NOT EXISTS idx_i18n_suggestions_score ON translations.i18n_suggestions (vote_score DESC);
CREATE INDEX IF NOT EXISTS idx_i18n_suggestions_user ON translations.i18n_suggestions (suggested_by);

COMMENT ON TABLE translations.i18n_suggestions IS
'Community-Übersetzungsvorschläge mit Voting-System';

-- ============================================================================
-- 5. i18n_suggestion_votes - Votes für Vorschläge
-- ============================================================================

CREATE TABLE IF NOT EXISTS translations.i18n_suggestion_votes (
    vote_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    suggestion_id UUID NOT NULL REFERENCES translations.i18n_suggestions(suggestion_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    vote_type VARCHAR(10) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (suggestion_id, user_id),
    CONSTRAINT chk_vote_type CHECK (vote_type IN ('up', 'down'))
);

CREATE INDEX IF NOT EXISTS idx_i18n_votes_suggestion ON translations.i18n_suggestion_votes (suggestion_id);
CREATE INDEX IF NOT EXISTS idx_i18n_votes_user ON translations.i18n_suggestion_votes (user_id);

-- ============================================================================
-- 6. i18n_translation_requests - On-Demand Übersetzungs-Anfragen
-- ============================================================================

CREATE TABLE IF NOT EXISTS translations.i18n_translation_requests (
    request_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Was soll übersetzt werden
    target_language VARCHAR(10) NOT NULL REFERENCES translations.supported_languages(language_code),

    -- Scope: 'full' (alle Keys), 'namespace' (ein Namespace), 'key' (einzelner Key)
    scope VARCHAR(20) NOT NULL DEFAULT 'full',
    namespace_id INTEGER REFERENCES translations.i18n_namespaces(namespace_id),
    key_id UUID REFERENCES translations.i18n_keys(key_id),

    -- Wer hat angefragt
    requested_by UUID REFERENCES core.users(user_id),
    requested_at TIMESTAMPTZ DEFAULT NOW(),

    -- Priorität (mehr Anfragen = höher)
    request_count INTEGER DEFAULT 1,
    priority INTEGER DEFAULT 0,

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'pending',

    -- Processing
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    keys_total INTEGER,
    keys_completed INTEGER DEFAULT 0,

    -- Error handling
    error_message TEXT,

    CONSTRAINT chk_request_status CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    CONSTRAINT chk_request_scope CHECK (scope IN ('full', 'namespace', 'key'))
);

CREATE INDEX IF NOT EXISTS idx_i18n_requests_lang ON translations.i18n_translation_requests (target_language);
CREATE INDEX IF NOT EXISTS idx_i18n_requests_status ON translations.i18n_translation_requests (status);
CREATE INDEX IF NOT EXISTS idx_i18n_requests_priority ON translations.i18n_translation_requests (priority DESC);

COMMENT ON TABLE translations.i18n_translation_requests IS
'On-Demand Übersetzungs-Anfragen für neue Sprachen';

-- ============================================================================
-- 7. Erweiterung supported_languages
-- ============================================================================

-- Neue Spalten hinzufügen
ALTER TABLE translations.supported_languages
    ADD COLUMN IF NOT EXISTS is_primary BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS priority INTEGER DEFAULT 100,
    ADD COLUMN IF NOT EXISTS fallback_language VARCHAR(10),
    ADD COLUMN IF NOT EXISTS auto_translate BOOLEAN DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS community_editable BOOLEAN DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS completion_percent DECIMAL(5,2) DEFAULT 0,
    ADD COLUMN IF NOT EXISTS total_keys INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS translated_keys INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS community_contributions INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- ============================================================================
-- 8. Primär-Sprachen setzen: DE → PL → EN
-- ============================================================================

UPDATE translations.supported_languages SET
    is_primary = TRUE,
    priority = 1,
    fallback_language = NULL,
    auto_translate = FALSE,
    community_editable = TRUE,
    updated_at = NOW()
WHERE language_code = 'de';

UPDATE translations.supported_languages SET
    is_primary = TRUE,
    priority = 2,
    fallback_language = 'de',
    auto_translate = FALSE,
    community_editable = TRUE,
    updated_at = NOW()
WHERE language_code = 'pl';

UPDATE translations.supported_languages SET
    is_primary = TRUE,
    priority = 3,
    fallback_language = 'de',
    auto_translate = FALSE,
    community_editable = TRUE,
    updated_at = NOW()
WHERE language_code = 'en';

-- Alle anderen Sprachen: Fallback auf DE, On-Demand
UPDATE translations.supported_languages SET
    is_primary = FALSE,
    fallback_language = 'de',
    auto_translate = TRUE,
    community_editable = TRUE,
    updated_at = NOW()
WHERE language_code NOT IN ('de', 'pl', 'en');

-- ============================================================================
-- 9. View: Übersetzungs-Fortschritt pro Sprache
-- ============================================================================

CREATE OR REPLACE VIEW v_i18n_language_progress AS
SELECT
    sl.language_code,
    sl.language_name,
    sl.native_name,
    sl.flag_emoji,
    sl.is_primary,
    sl.priority,
    sl.fallback_language,
    sl.active,
    COUNT(DISTINCT ik.key_id) AS total_keys,
    COUNT(DISTINCT it.key_id) AS translated_keys,
    CASE
        WHEN COUNT(DISTINCT ik.key_id) > 0
        THEN ROUND((COUNT(DISTINCT it.key_id)::DECIMAL / COUNT(DISTINCT ik.key_id) * 100), 2)
        ELSE 0
    END AS completion_percent,
    COUNT(DISTINCT CASE WHEN it.is_verified THEN it.key_id END) AS verified_keys,
    COUNT(DISTINCT isug.suggestion_id) FILTER (WHERE isug.status = 'pending') AS pending_suggestions
FROM translations.supported_languages sl
CROSS JOIN translations.i18n_keys ik
LEFT JOIN translations.i18n_translations it ON ik.key_id = it.key_id AND sl.language_code = it.language_code
LEFT JOIN translations.i18n_suggestions isug ON it.translation_id = isug.translation_id
GROUP BY sl.language_code, sl.language_name, sl.native_name, sl.flag_emoji,
         sl.is_primary, sl.priority, sl.fallback_language, sl.active
ORDER BY sl.priority, sl.language_name;

COMMENT ON VIEW v_i18n_language_progress IS
'Übersetzungs-Fortschritt pro Sprache mit Statistiken';

-- ============================================================================
-- 10. View: Fehlende Übersetzungen
-- ============================================================================

CREATE OR REPLACE VIEW v_i18n_missing_translations AS
SELECT
    sl.language_code,
    sl.language_name,
    ns.namespace_code,
    ik.key_id,
    ik.key_path,
    ik.context,
    de_trans.value AS german_value
FROM translations.supported_languages sl
CROSS JOIN translations.i18n_keys ik
JOIN translations.i18n_namespaces ns ON ik.namespace_id = ns.namespace_id
LEFT JOIN translations.i18n_translations it ON ik.key_id = it.key_id AND sl.language_code = it.language_code
LEFT JOIN translations.i18n_translations de_trans ON ik.key_id = de_trans.key_id AND de_trans.language_code = 'de'
WHERE sl.active = TRUE
  AND it.translation_id IS NULL
ORDER BY sl.priority, ns.sort_order, ik.key_path;

COMMENT ON VIEW v_i18n_missing_translations IS
'Alle fehlenden Übersetzungen mit deutschem Referenztext';

-- ============================================================================
-- 11. Function: Bundle für Sprache abrufen
-- ============================================================================

CREATE OR REPLACE FUNCTION get_i18n_bundle(
    p_language_code VARCHAR(10),
    p_namespace_code VARCHAR(50) DEFAULT NULL
)
RETURNS JSONB AS $$
DECLARE
    v_result JSONB := '{}';
    v_fallback VARCHAR(10);
BEGIN
    -- Fallback-Sprache ermitteln
    SELECT fallback_language INTO v_fallback
    FROM translations.supported_languages
    WHERE language_code = p_language_code;

    -- Translations sammeln (mit Fallback)
    SELECT jsonb_object_agg(
        ns.namespace_code || '.' || ik.key_path,
        COALESCE(it.value, fb.value, ik.key_path)
    ) INTO v_result
    FROM translations.i18n_keys ik
    JOIN translations.i18n_namespaces ns ON ik.namespace_id = ns.namespace_id
    LEFT JOIN translations.i18n_translations it ON ik.key_id = it.key_id AND it.language_code = p_language_code
    LEFT JOIN translations.i18n_translations fb ON ik.key_id = fb.key_id AND fb.language_code = v_fallback
    WHERE (p_namespace_code IS NULL OR ns.namespace_code = p_namespace_code)
      AND ns.is_active = TRUE;

    RETURN COALESCE(v_result, '{}');
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_i18n_bundle IS
'Gibt alle Übersetzungen für eine Sprache als JSONB zurück (mit Fallback)';

-- ============================================================================
-- 12. Trigger: Vote-Counter aktualisieren
-- ============================================================================

CREATE OR REPLACE FUNCTION update_suggestion_vote_counts()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF NEW.vote_type = 'up' THEN
            UPDATE translations.i18n_suggestions SET votes_up = votes_up + 1 WHERE suggestion_id = NEW.suggestion_id;
        ELSE
            UPDATE translations.i18n_suggestions SET votes_down = votes_down + 1 WHERE suggestion_id = NEW.suggestion_id;
        END IF;
    ELSIF TG_OP = 'DELETE' THEN
        IF OLD.vote_type = 'up' THEN
            UPDATE translations.i18n_suggestions SET votes_up = votes_up - 1 WHERE suggestion_id = OLD.suggestion_id;
        ELSE
            UPDATE translations.i18n_suggestions SET votes_down = votes_down - 1 WHERE suggestion_id = OLD.suggestion_id;
        END IF;
    ELSIF TG_OP = 'UPDATE' THEN
        -- Vote geändert
        IF OLD.vote_type = 'up' THEN
            UPDATE translations.i18n_suggestions SET votes_up = votes_up - 1 WHERE suggestion_id = OLD.suggestion_id;
        ELSE
            UPDATE translations.i18n_suggestions SET votes_down = votes_down - 1 WHERE suggestion_id = OLD.suggestion_id;
        END IF;
        IF NEW.vote_type = 'up' THEN
            UPDATE translations.i18n_suggestions SET votes_up = votes_up + 1 WHERE suggestion_id = NEW.suggestion_id;
        ELSE
            UPDATE translations.i18n_suggestions SET votes_down = votes_down + 1 WHERE suggestion_id = NEW.suggestion_id;
        END IF;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_suggestion_votes
    AFTER INSERT OR UPDATE OR DELETE ON translations.i18n_suggestion_votes
    FOR EACH ROW EXECUTE FUNCTION update_suggestion_vote_counts();

-- ============================================================================
-- 13. Trigger: updated_at
-- ============================================================================

CREATE TRIGGER update_i18n_namespaces_updated_at BEFORE UPDATE ON translations.i18n_namespaces
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_i18n_keys_updated_at BEFORE UPDATE ON translations.i18n_keys
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_i18n_translations_updated_at BEFORE UPDATE ON translations.i18n_translations
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 14. i18n_ai_reviews - KI-Moderation für Übersetzungen
-- ============================================================================

CREATE TABLE IF NOT EXISTS translations.i18n_ai_reviews (
    review_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Was wurde geprüft
    translation_id UUID REFERENCES translations.i18n_translations(translation_id) ON DELETE CASCADE,
    suggestion_id UUID REFERENCES translations.i18n_suggestions(suggestion_id) ON DELETE CASCADE,

    -- KI-Modell das geprüft hat
    ai_model VARCHAR(100) NOT NULL,  -- 'gpt-5.2', 'claude-opus-4', etc.
    ai_provider VARCHAR(50) NOT NULL, -- 'openai', 'anthropic'

    -- Bewertung
    quality_score DECIMAL(3,2),  -- 0.00 - 1.00
    accuracy_score DECIMAL(3,2), -- Genauigkeit der Übersetzung
    fluency_score DECIMAL(3,2),  -- Natürlichkeit/Flüssigkeit
    consistency_score DECIMAL(3,2), -- Konsistenz mit anderen Übersetzungen

    -- Empfehlung
    recommendation VARCHAR(20) NOT NULL, -- 'approve', 'reject', 'needs_review', 'improve'

    -- Verbesserungsvorschlag der KI
    ai_suggestion TEXT,
    ai_explanation TEXT,

    -- Probleme gefunden
    issues JSONB DEFAULT '[]', -- [{"type": "grammar", "text": "...", "suggestion": "..."}]

    -- Tokens/Kosten
    tokens_used INTEGER,
    cost_eur DECIMAL(10,6),

    -- Meta
    reviewed_at TIMESTAMPTZ DEFAULT NOW(),
    response_time_ms INTEGER,

    CONSTRAINT chk_ai_recommendation CHECK (recommendation IN ('approve', 'reject', 'needs_review', 'improve')),
    CONSTRAINT chk_review_ref CHECK (translation_id IS NOT NULL OR suggestion_id IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_ai_reviews_translation ON translations.i18n_ai_reviews (translation_id);
CREATE INDEX IF NOT EXISTS idx_ai_reviews_suggestion ON translations.i18n_ai_reviews (suggestion_id);
CREATE INDEX IF NOT EXISTS idx_ai_reviews_recommendation ON translations.i18n_ai_reviews (recommendation);
CREATE INDEX IF NOT EXISTS idx_ai_reviews_model ON translations.i18n_ai_reviews (ai_model);

COMMENT ON TABLE translations.i18n_ai_reviews IS
'KI-Moderation für Übersetzungen und Community-Vorschläge';

-- ============================================================================
-- 15. i18n_moderation_queue - Moderations-Warteschlange
-- ============================================================================

CREATE TABLE IF NOT EXISTS translations.i18n_moderation_queue (
    queue_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Was soll moderiert werden
    item_type VARCHAR(20) NOT NULL, -- 'translation', 'suggestion'
    translation_id UUID REFERENCES translations.i18n_translations(translation_id) ON DELETE CASCADE,
    suggestion_id UUID REFERENCES translations.i18n_suggestions(suggestion_id) ON DELETE CASCADE,

    -- Priorität (höher = dringender)
    priority INTEGER DEFAULT 0,

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'pending',

    -- Moderation (KI oder Mensch)
    moderation_type VARCHAR(20), -- 'ai', 'human', 'ai_then_human'

    -- KI-Review (falls vorhanden)
    ai_review_id UUID REFERENCES translations.i18n_ai_reviews(review_id),

    -- Human-Review (falls nötig)
    assigned_to UUID REFERENCES core.users(user_id),
    human_decision VARCHAR(20),
    human_comment TEXT,

    -- Timing
    created_at TIMESTAMPTZ DEFAULT NOW(),
    ai_reviewed_at TIMESTAMPTZ,
    human_reviewed_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    CONSTRAINT chk_queue_item_type CHECK (item_type IN ('translation', 'suggestion')),
    CONSTRAINT chk_queue_status CHECK (status IN ('pending', 'ai_reviewing', 'awaiting_human', 'completed', 'skipped')),
    CONSTRAINT chk_moderation_type CHECK (moderation_type IN ('ai', 'human', 'ai_then_human'))
);

CREATE INDEX IF NOT EXISTS idx_moderation_queue_status ON translations.i18n_moderation_queue (status);
CREATE INDEX IF NOT EXISTS idx_moderation_queue_priority ON translations.i18n_moderation_queue (priority DESC, created_at);
CREATE INDEX IF NOT EXISTS idx_moderation_queue_assigned ON translations.i18n_moderation_queue (assigned_to) WHERE assigned_to IS NOT NULL;

COMMENT ON TABLE translations.i18n_moderation_queue IS
'Warteschlange für KI- und Human-Moderation von Übersetzungen';

-- ============================================================================
-- 16. i18n_ai_config - KI-Konfiguration für Moderation
-- ============================================================================

CREATE TABLE IF NOT EXISTS translations.i18n_ai_config (
    config_id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by UUID REFERENCES core.users(user_id)
);

-- Standard-Konfiguration
INSERT INTO translations.i18n_ai_config (config_key, config_value, description) VALUES
    ('moderation_model', '"gpt-4o"', 'Standard-Modell für Moderation'),
    ('auto_approve_threshold', '0.95', 'Ab diesem Score automatisch genehmigen'),
    ('auto_reject_threshold', '0.3', 'Unter diesem Score automatisch ablehnen'),
    ('human_review_threshold', '0.7', 'Zwischen reject und approve: Human Review'),
    ('moderation_prompt', '{
        "system": "Du bist ein Übersetzungs-Moderator für eine Lernplattform. Prüfe Übersetzungen auf Qualität, Genauigkeit und Konsistenz.",
        "criteria": [
            "Grammatik und Rechtschreibung",
            "Fachliche Korrektheit",
            "Natürlicher Sprachfluss",
            "Konsistenz mit Fachbegriffen",
            "Passender Ton für Lernplattform"
        ]
    }', 'Prompt-Template für KI-Moderation'),
    ('batch_size', '50', 'Anzahl Übersetzungen pro Batch-Review'),
    ('enabled_languages', '["de", "pl", "en"]', 'Sprachen für KI-Moderation aktiviert')
ON CONFLICT (config_key) DO UPDATE SET
    config_value = EXCLUDED.config_value,
    updated_at = NOW();

COMMENT ON TABLE translations.i18n_ai_config IS
'Konfiguration für KI-gestützte Übersetzungsmoderation';

-- ============================================================================
-- 17. View: Moderations-Dashboard
-- ============================================================================

CREATE OR REPLACE VIEW v_i18n_moderation_dashboard AS
SELECT
    sl.language_code,
    sl.language_name,
    sl.flag_emoji,
    COUNT(DISTINCT mq.queue_id) FILTER (WHERE mq.status = 'pending') AS pending_count,
    COUNT(DISTINCT mq.queue_id) FILTER (WHERE mq.status = 'ai_reviewing') AS ai_reviewing_count,
    COUNT(DISTINCT mq.queue_id) FILTER (WHERE mq.status = 'awaiting_human') AS awaiting_human_count,
    COUNT(DISTINCT isug.suggestion_id) FILTER (WHERE isug.status = 'pending') AS pending_suggestions,
    COUNT(DISTINCT ar.review_id) FILTER (WHERE ar.reviewed_at > NOW() - INTERVAL '24 hours') AS ai_reviews_24h,
    AVG(ar.quality_score) FILTER (WHERE ar.reviewed_at > NOW() - INTERVAL '7 days') AS avg_quality_7d
FROM translations.supported_languages sl
LEFT JOIN translations.i18n_translations it ON sl.language_code = it.language_code
LEFT JOIN translations.i18n_moderation_queue mq ON it.translation_id = mq.translation_id
LEFT JOIN translations.i18n_suggestions isug ON it.translation_id = isug.translation_id
LEFT JOIN translations.i18n_ai_reviews ar ON it.translation_id = ar.translation_id
WHERE sl.active = TRUE
GROUP BY sl.language_code, sl.language_name, sl.flag_emoji
ORDER BY pending_count DESC;

COMMENT ON VIEW v_i18n_moderation_dashboard IS
'Dashboard für Übersetzungs-Moderation mit KI-Statistiken';

-- ============================================================================
-- Migration 072 abgeschlossen
-- ============================================================================
-- Neue Tabellen: i18n_namespaces, i18n_keys, i18n_translations,
--                i18n_suggestions, i18n_suggestion_votes, i18n_translation_requests,
--                i18n_ai_reviews, i18n_moderation_queue, i18n_ai_config
-- Erweitert: supported_languages
-- Views: v_i18n_language_progress, v_i18n_missing_translations, v_i18n_moderation_dashboard
-- Functions: get_i18n_bundle()
-- Primär-Sprachen: DE (1), PL (2), EN (3)
-- KI-Moderation: GPT-4o/GPT-5.2 für automatische Review
-- ============================================================================
