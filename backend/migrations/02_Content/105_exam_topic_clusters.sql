-- Exam Topic Clusters: configurable per exam type
-- Hybrid approach: admin-managed clusters override dynamic auto-clustering
CREATE TABLE IF NOT EXISTS assessments.exam_topic_clusters (
    cluster_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_type_key VARCHAR(50) NOT NULL,
    cluster_key VARCHAR(100) NOT NULL,
    label JSONB NOT NULL DEFAULT '{}',
    topics TEXT[] NOT NULL DEFAULT '{}',
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(exam_type_key, cluster_key)
);

CREATE INDEX IF NOT EXISTS idx_exam_topic_clusters_type
    ON assessments.exam_topic_clusters(exam_type_key);

-- Seed: FISI AP1 clusters (migrated from hardcoded exam_topic_clusters.py)
INSERT INTO assessments.exam_topic_clusters (exam_type_key, cluster_key, label, topics, sort_order)
VALUES
    ('IHK_FISI_AP1', 'netzwerktechnik',
     '{"de": "Netzwerktechnik", "en": "Network Technology"}',
     ARRAY['netzwerk','routing','subnetting','wlan','firewall','dhcp','osi_modell','vpn','gateway','ipv4','netzwerkkonfiguration','netzwerksicherheit','dns'],
     1),
    ('IHK_FISI_AP1', 'projektmanagement',
     '{"de": "Projektmanagement & Kalkulation", "en": "Project Management & Costing"}',
     ARRAY['kalkulation','projektmanagement','qualitaetsmanagement','energiekosten','netzplan','gantt'],
     2),
    ('IHK_FISI_AP1', 'it_sicherheit',
     '{"de": "IT-Sicherheit & Datenschutz", "en": "IT Security & Data Protection"}',
     ARRAY['it_sicherheit','verschluesselung','datenschutz','backup','schutzbedarfsanalyse','dsgvo','malware','it_sicherheit_datenschutz'],
     3),
    ('IHK_FISI_AP1', 'datenbanken',
     '{"de": "Datenbanken & SQL", "en": "Databases & SQL"}',
     ARRAY['datenbanken','sql','erm','relationenmodell','normalisierung'],
     4),
    ('IHK_FISI_AP1', 'programmierung',
     '{"de": "Programmierung & Softwareentwicklung", "en": "Programming & Software Development"}',
     ARRAY['programmierung','software','code','html','java','python','csv','json','xml','datenexport','datenkategorisierung','pseudocode','algorithmen','softwareentwicklung_datenmanagement'],
     5),
    ('IHK_FISI_AP1', 'wirtschaft',
     '{"de": "Wirtschaft & Recht (WiSo)", "en": "Business & Law"}',
     ARRAY['wirtschaft','arbeitsrecht','rechtsformen','vertragsrecht','organisationsformen','markt','unternehmensgruendung','unternehmensgründung','organisationsstruktur','organigramm','einliniensystem','home_office','ausbildung','wirtschafts_geschaeftsprozesse','rechtliche_organisatorische_grundlagen'],
     6),
    ('IHK_FISI_AP1', 'it_systeme',
     '{"de": "IT-Systeme & Hardware", "en": "IT Systems & Hardware"}',
     ARRAY['hardware','cloud','virtualisierung','raid','itil','fehleranalyse','speicher','cpu','it_systeme_betrieb'],
     7)
ON CONFLICT (exam_type_key, cluster_key) DO NOTHING;
