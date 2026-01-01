-- ============================================================================
-- Migration 069: System-Features Tabellen
-- ============================================================================
--
-- Referenz: 02a_System-Features.md
--
-- System-Features sind keine Content-Lernmethoden, sondern eigenständige
-- Infrastruktur-/Service-Module rund um die Lernmethoden.
--
-- Feature-Bereiche:
-- 1. TutorAgent (LM04, LM07) - KI-gestützte Tutor-Funktionen
-- 2. CourseFeatures (LM05) - Kursweite Visualisierungen (Mindmaps)
-- 3. IT-Umgebungen (LM09-LM11, LM16) - Sandboxes, Simulationen
-- 4. Kollaboration (LM26-LM32) - Peer Review, Team-Case, Lerntagebuch
-- 5. Gamification - XP, Quests, Spaced Repetition (aus LM30, LM31)
--
-- ============================================================================

-- ============================================================================
-- 1. system_feature_types - Definiert alle verfügbaren System-Features
-- ============================================================================

CREATE TABLE IF NOT EXISTS system_feature_types (
    feature_type_id SERIAL PRIMARY KEY,
    feature_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(30) NOT NULL,
    description TEXT,
    former_lm_id INTEGER,
    config_schema JSONB,
    is_premium BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_feature_category CHECK (category IN (
        'tutor', 'visualization', 'it_sandbox', 'collaboration', 'gamification'
    ))
);

CREATE INDEX IF NOT EXISTS idx_system_feature_types_category ON system_feature_types(category);
CREATE INDEX IF NOT EXISTS idx_system_feature_types_active ON system_feature_types(is_active) WHERE is_active = TRUE;

COMMENT ON TABLE system_feature_types IS
'System-Feature-Typen (frühere LMs, jetzt eigenständige Module).
Kategorien: tutor, visualization, it_sandbox, collaboration, gamification.
Referenz: 02a_System-Features.md';

-- ============================================================================
-- 2. Standard System-Feature-Typen (frühere LMs, jetzt eigenständige Module)
-- Referenz: CLAUDE.md und 02a_System-Features.md
-- ============================================================================

INSERT INTO system_feature_types (feature_code, name, category, description, former_lm_id, is_premium, is_active)
VALUES
    -- Tutor-Features (TutorAgent)
    ('socratic_dialog', 'Sokratischer Dialog', 'tutor',
     'KI-geführter Dialog mit Gegenfragen statt direkten Antworten. Fördert eigenständiges Denken.',
     4, FALSE, TRUE),
    ('npc_tutor', 'NPC-Tutor-Lecture', 'tutor',
     'Interaktiver virtueller Tutor mit Persona, der Themen erklärt und auf Fragen eingeht.',
     7, TRUE, TRUE),

    -- Visualization-Features (CourseFeatures)
    ('mindmap_generator', 'Mindmap-Generator', 'visualization',
     'Automatische Generierung von Mindmaps aus Kapitel-/Kursinhalt.',
     5, FALSE, TRUE),
    ('glossary_auto', 'Glossar-Autogenerator', 'visualization',
     'Automatische Erstellung eines Glossars aus Fachbegriffen im Kursinhalt.',
     NULL, FALSE, TRUE),

    -- IT-Sandbox-Features
    ('code_sandbox', 'Code/Config Sandbox', 'it_sandbox',
     'Interaktive Sandbox für Code und Konfigurationsdateien.',
     9, TRUE, TRUE),
    ('network_simulation', 'Netzwerk-Simulation', 'it_sandbox',
     'Drag-and-Drop Netzwerkaufbau mit Router, Switch, Firewall-Elementen.',
     10, TRUE, TRUE),
    ('it_scenario', 'IT-Szenario lösen', 'it_sandbox',
     'KI-generierte IT-Problemszenarien mit schrittweiser Lösungsfindung.',
     11, TRUE, TRUE),
    ('error_analysis', 'Fehleranalyse', 'it_sandbox',
     'Systematische Analyse von Fehlern in Code, Logs oder Konfigurationen.',
     16, TRUE, TRUE),

    -- Gamification-Features
    ('xp_system', 'XP/Level-System', 'gamification',
     'Experience Points und Level-Aufstieg für Lernfortschritt.',
     NULL, FALSE, TRUE),
    ('quests', 'Quest-System', 'gamification',
     'Daily Quests und Achievements für zusätzliche Motivation.',
     31, TRUE, TRUE),
    ('spaced_repetition', 'Spaced Repetition', 'gamification',
     'SM-2 basierte Wiederholungen für nachhaltiges Lernen.',
     30, FALSE, TRUE),
    ('daily_streak', 'Daily Streak', 'gamification',
     'Tägliche Lernstreak-Zählung mit Belohnungen.',
     NULL, FALSE, TRUE),

    -- Adaptive-Features
    ('adaptive_difficulty', 'Adaptive Schwierigkeit', 'gamification',
     'Automatische Anpassung der Aufgabenschwierigkeit basierend auf Lernfortschritt.',
     26, TRUE, TRUE),
    ('adaptive_path', 'Lernpfad-Autogenerator', 'gamification',
     'KI-gesteuerte Empfehlungen für optimalen Lernpfad.',
     27, TRUE, TRUE)

ON CONFLICT (feature_code) DO UPDATE SET
    name = EXCLUDED.name,
    category = EXCLUDED.category,
    description = EXCLUDED.description,
    former_lm_id = EXCLUDED.former_lm_id,
    is_premium = EXCLUDED.is_premium,
    updated_at = NOW();

-- ============================================================================
-- 3. course_features - Feature-Aktivierung pro Kurs
-- ============================================================================

CREATE TABLE IF NOT EXISTS course_features (
    course_feature_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    feature_type_id INTEGER NOT NULL REFERENCES system_feature_types(feature_type_id),
    is_enabled BOOLEAN DEFAULT TRUE,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (course_id, feature_type_id)
);

CREATE INDEX IF NOT EXISTS idx_course_features_course ON course_features(course_id);
CREATE INDEX IF NOT EXISTS idx_course_features_type ON course_features(feature_type_id);
CREATE INDEX IF NOT EXISTS idx_course_features_enabled ON course_features(is_enabled) WHERE is_enabled = TRUE;

COMMENT ON TABLE course_features IS
'System-Features aktiviert pro Kurs. Konfiguration in config (JSONB).';

-- ============================================================================
-- 4. tutor_sessions - Sessions für TutorAgent (Sokratisch, NPC)
-- ============================================================================

CREATE TABLE IF NOT EXISTS tutor_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(course_id) ON DELETE SET NULL,
    chapter_id UUID REFERENCES chapters(chapter_id) ON DELETE SET NULL,
    feature_type_id INTEGER NOT NULL REFERENCES system_feature_types(feature_type_id),
    persona_config JSONB,
    session_state JSONB DEFAULT '{}',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    tokens_used INTEGER DEFAULT 0,
    message_count INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_tutor_sessions_user ON tutor_sessions(user_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_tutor_sessions_course ON tutor_sessions(course_id);
CREATE INDEX IF NOT EXISTS idx_tutor_sessions_active ON tutor_sessions(ended_at) WHERE ended_at IS NULL;

COMMENT ON TABLE tutor_sessions IS
'Sessions für TutorAgent (Sokratischer Dialog, NPC-Tutor).
Speichert Kontext und Gesprächsverlauf.';

-- ============================================================================
-- 5. tutor_messages - Nachrichten innerhalb einer Tutor-Session
-- ============================================================================

CREATE TABLE IF NOT EXISTS tutor_messages (
    message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES tutor_sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_tutor_message_role CHECK (role IN ('user', 'tutor', 'system'))
);

CREATE INDEX IF NOT EXISTS idx_tutor_messages_session ON tutor_messages(session_id, created_at);

COMMENT ON TABLE tutor_messages IS 'Nachrichten in Tutor-Sessions.';

-- ============================================================================
-- 6. it_sandbox_instances - Laufende IT-Sandbox-Umgebungen
-- ============================================================================

CREATE TABLE IF NOT EXISTS it_sandbox_instances (
    instance_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(course_id) ON DELETE SET NULL,
    lesson_id UUID REFERENCES lessons(lesson_id) ON DELETE SET NULL,
    feature_type_id INTEGER NOT NULL REFERENCES system_feature_types(feature_type_id),
    sandbox_type VARCHAR(30) NOT NULL,
    config JSONB NOT NULL DEFAULT '{}',
    state JSONB DEFAULT '{}',
    container_id VARCHAR(100),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    CONSTRAINT chk_sandbox_type CHECK (sandbox_type IN (
        'code', 'config', 'network', 'troubleshooting', 'error_analysis'
    ))
);

CREATE INDEX IF NOT EXISTS idx_it_sandbox_user ON it_sandbox_instances(user_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_it_sandbox_active ON it_sandbox_instances(ended_at) WHERE ended_at IS NULL;

COMMENT ON TABLE it_sandbox_instances IS
'IT-Sandbox-Instanzen (Code, Config, Netzwerk-Simulation).
Container-ID für verbundene Docker/K8s-Umgebung.';

-- ============================================================================
-- 7. peer_review_tasks - Peer Review Aufgaben
-- ============================================================================

CREATE TABLE IF NOT EXISTS peer_review_tasks (
    task_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    chapter_id UUID REFERENCES chapters(chapter_id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    instructions TEXT,
    rubric JSONB NOT NULL DEFAULT '[]',
    due_date TIMESTAMPTZ,
    reviews_required INTEGER DEFAULT 2,
    is_anonymous BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_peer_review_tasks_course ON peer_review_tasks(course_id);

COMMENT ON TABLE peer_review_tasks IS
'Peer Review Aufgaben mit Rubric-Definition.';

-- ============================================================================
-- 8. peer_review_submissions - Einreichungen für Peer Review
-- ============================================================================

CREATE TABLE IF NOT EXISTS peer_review_submissions (
    submission_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES peer_review_tasks(task_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    attachments JSONB DEFAULT '[]',
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (task_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_peer_submissions_task ON peer_review_submissions(task_id);
CREATE INDEX IF NOT EXISTS idx_peer_submissions_user ON peer_review_submissions(user_id);

-- ============================================================================
-- 9. peer_review_ratings - Bewertungen von Peer-Arbeiten
-- ============================================================================

CREATE TABLE IF NOT EXISTS peer_review_ratings (
    rating_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL REFERENCES peer_review_submissions(submission_id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    rubric_scores JSONB NOT NULL DEFAULT '{}',
    overall_score DECIMAL(5,2),
    feedback TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (submission_id, reviewer_id)
);

CREATE INDEX IF NOT EXISTS idx_peer_ratings_submission ON peer_review_ratings(submission_id);
CREATE INDEX IF NOT EXISTS idx_peer_ratings_reviewer ON peer_review_ratings(reviewer_id);

-- ============================================================================
-- 10. learning_journals - Lerntagebuch-Einträge
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_journals (
    entry_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(course_id) ON DELETE SET NULL,
    chapter_id UUID REFERENCES chapters(chapter_id) ON DELETE SET NULL,
    title VARCHAR(255),
    content TEXT NOT NULL,
    reflection_type VARCHAR(30) DEFAULT 'general',
    mood_rating INTEGER,
    tags JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_reflection_type CHECK (reflection_type IN (
        'general', 'lesson', 'exam', 'project', 'challenge', 'success'
    )),
    CONSTRAINT chk_mood_rating CHECK (mood_rating BETWEEN 1 AND 5)
);

CREATE INDEX IF NOT EXISTS idx_learning_journals_user ON learning_journals(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_learning_journals_course ON learning_journals(course_id);
CREATE INDEX IF NOT EXISTS idx_learning_journals_tags ON learning_journals USING GIN(tags);

COMMENT ON TABLE learning_journals IS
'Lerntagebuch-Einträge für Reflexion. Mood 1-5 = Frustration bis Erfolg.';

-- ============================================================================
-- 11. portfolio_items - Portfolio-Artefakte
-- ============================================================================

CREATE TABLE IF NOT EXISTS portfolio_items (
    item_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(course_id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    item_type VARCHAR(30) NOT NULL,
    content JSONB DEFAULT '{}',
    file_path VARCHAR(500),
    meta_comment TEXT,
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_item_type CHECK (item_type IN (
        'document', 'code', 'diagram', 'presentation', 'project', 'certificate', 'other'
    ))
);

CREATE INDEX IF NOT EXISTS idx_portfolio_user ON portfolio_items(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_portfolio_featured ON portfolio_items(is_featured) WHERE is_featured = TRUE;

COMMENT ON TABLE portfolio_items IS
'Portfolio-Artefakte. is_featured für Highlight-Items.';

-- ============================================================================
-- 12. team_cases - Team-Case / Gruppenfallarbeit
-- ============================================================================

CREATE TABLE IF NOT EXISTS team_cases (
    case_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    scenario JSONB NOT NULL DEFAULT '{}',
    roles JSONB DEFAULT '[]',
    deliverables JSONB DEFAULT '[]',
    due_date TIMESTAMPTZ,
    max_team_size INTEGER DEFAULT 5,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_team_cases_course ON team_cases(course_id);

-- ============================================================================
-- 13. team_case_teams - Teams für Fallarbeit
-- ============================================================================

CREATE TABLE IF NOT EXISTS team_case_teams (
    team_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID NOT NULL REFERENCES team_cases(case_id) ON DELETE CASCADE,
    team_name VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 14. team_case_members - Team-Mitglieder mit Rollen
-- ============================================================================

CREATE TABLE IF NOT EXISTS team_case_members (
    member_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID NOT NULL REFERENCES team_case_teams(team_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    role_in_case VARCHAR(50),
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (team_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_team_case_members_user ON team_case_members(user_id);

-- ============================================================================
-- 15. gamification_progress - XP, Level, Streaks
-- ============================================================================

CREATE TABLE IF NOT EXISTS gamification_progress (
    progress_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE UNIQUE,
    total_xp INTEGER DEFAULT 0,
    current_level INTEGER DEFAULT 1,
    daily_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    achievements JSONB DEFAULT '[]',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_gamification_level ON gamification_progress(current_level DESC);
CREATE INDEX IF NOT EXISTS idx_gamification_xp ON gamification_progress(total_xp DESC);

COMMENT ON TABLE gamification_progress IS
'Gamification-Fortschritt pro User (XP, Level, Streaks).';

-- ============================================================================
-- 16. spaced_repetition_items - Items für Wiederholung
-- ============================================================================

CREATE TABLE IF NOT EXISTS spaced_repetition_items (
    item_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    source_type VARCHAR(30) NOT NULL,
    source_id UUID NOT NULL,
    content_hash VARCHAR(64),
    ease_factor DECIMAL(4,2) DEFAULT 2.5,
    interval_days INTEGER DEFAULT 1,
    repetitions INTEGER DEFAULT 0,
    next_review_date DATE NOT NULL,
    last_reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_source_type CHECK (source_type IN (
        'flashcard', 'quiz_question', 'learning_method', 'custom'
    ))
);

CREATE INDEX IF NOT EXISTS idx_sr_items_user_next ON spaced_repetition_items(user_id, next_review_date);
CREATE INDEX IF NOT EXISTS idx_sr_items_source ON spaced_repetition_items(source_type, source_id);

COMMENT ON TABLE spaced_repetition_items IS
'Items für Spaced Repetition (SM-2 Algorithmus).
ease_factor: 1.3-3.0, interval_days: nächster Review-Abstand.';

-- ============================================================================
-- Trigger für updated_at
-- ============================================================================

CREATE TRIGGER update_system_feature_types_updated_at BEFORE UPDATE ON system_feature_types
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_course_features_updated_at BEFORE UPDATE ON course_features
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_peer_review_tasks_updated_at BEFORE UPDATE ON peer_review_tasks
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_learning_journals_updated_at BEFORE UPDATE ON learning_journals
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_portfolio_items_updated_at BEFORE UPDATE ON portfolio_items
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_team_cases_updated_at BEFORE UPDATE ON team_cases
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_gamification_progress_updated_at BEFORE UPDATE ON gamification_progress
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Migration 069 abgeschlossen
-- ============================================================================
