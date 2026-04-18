-- ============================================================================
-- Migration: 121_ap2_topic_occurrences.sql
-- Description: AP2 Topic-Vorkommen pro Prüfung als Source-of-Truth für die
--              bereich-Zuordnung (PB2/PB3/WISO/both). Macht aus
--              ap2_topics.bereich ein berechnetes Aggregat statt Schätzung.
--
--              Vorteile:
--              - Audit-Trail: pro Topic sieht man WO+WANN es vorkam
--              - Auto-Recompute bei neuen Prüfungen
--              - Sanity-Check: pro Termin/Bereich = 90 Punkte
--              - Frontend kann Quellen-Liste anzeigen
--
--              Seed: 74 Occurrences aus S2022, W2022/23, S2023, W2023/24, S2024
--              (5 Termine × PB2+PB3 = 10 Prüfungen, je 90 Punkte)
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-04-18
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. TABELLE
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS assessments.ap2_topic_exam_occurrences (
    occurrence_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_id        UUID NOT NULL REFERENCES assessments.ap2_topics(topic_id) ON DELETE CASCADE,
    exam_term       VARCHAR(20) NOT NULL,            -- 'S2022', 'W2023', ...
    bereich         VARCHAR(10) NOT NULL CHECK (bereich IN ('PB2','PB3','WISO')),
    aufgabe_nummer  VARCHAR(20) NOT NULL,            -- '1.1', '2.4.3', '3.a'
    points          NUMERIC(5,2) NOT NULL CHECK (points > 0),
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (topic_id, exam_term, aufgabe_nummer)
);

CREATE INDEX IF NOT EXISTS idx_ap2_occurrences_topic
    ON assessments.ap2_topic_exam_occurrences (topic_id);
CREATE INDEX IF NOT EXISTS idx_ap2_occurrences_term
    ON assessments.ap2_topic_exam_occurrences (exam_term, bereich);

COMMENT ON TABLE assessments.ap2_topic_exam_occurrences IS
    'Source-of-Truth: pro Topic+Prüfung+Aufgabe — wo+wieviele Punkte. '
    'Treibt automatische bereich-Zuordnung in ap2_topics via compute_ap2_topic_bereich().';

-- ---------------------------------------------------------------------------
-- 2. COMPUTE-FUNKTION für bereich aus Occurrences
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION assessments.compute_ap2_topic_bereich(p_topic_id UUID)
RETURNS TEXT AS $$
DECLARE
    pb2_pts NUMERIC := 0;
    pb3_pts NUMERIC := 0;
    wiso_pts NUMERIC := 0;
    fallback TEXT;
BEGIN
    SELECT
        COALESCE(SUM(points) FILTER (WHERE bereich = 'PB2'),  0),
        COALESCE(SUM(points) FILTER (WHERE bereich = 'PB3'),  0),
        COALESCE(SUM(points) FILTER (WHERE bereich = 'WISO'), 0)
    INTO pb2_pts, pb3_pts, wiso_pts
    FROM assessments.ap2_topic_exam_occurrences
    WHERE topic_id = p_topic_id;

    -- Keine Daten → bestehenden Wert behalten (z.B. WISO-Themen ohne Occurrences)
    IF pb2_pts + pb3_pts + wiso_pts = 0 THEN
        SELECT bereich INTO fallback FROM assessments.ap2_topics WHERE topic_id = p_topic_id;
        RETURN COALESCE(fallback, 'PB2');
    END IF;

    -- WISO dominant
    IF wiso_pts > pb2_pts + pb3_pts THEN
        RETURN 'WISO';
    END IF;

    -- "both" wenn das kleinere mind. 30% des größeren ist
    IF pb2_pts > 0 AND pb3_pts > 0
       AND LEAST(pb2_pts, pb3_pts) / GREATEST(pb2_pts, pb3_pts) >= 0.3
    THEN
        RETURN 'both';
    END IF;

    IF pb2_pts >= pb3_pts THEN
        RETURN 'PB2';
    ELSE
        RETURN 'PB3';
    END IF;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION assessments.compute_ap2_topic_bereich IS
    'Berechnet primären Bereich (PB2/PB3/WISO/both) eines Topics aus seinen '
    'Vorkommen. "both" wenn kleinerer Bereich >= 30 %% des größeren.';

-- ---------------------------------------------------------------------------
-- 3. SEED — 74 Occurrences aus 10 echten Prüfungen
--          Punkte pro Termin/Bereich validiert: jeweils 90P
-- ---------------------------------------------------------------------------

WITH topic_lookup AS (
    SELECT slug, topic_id FROM assessments.ap2_topics
)
INSERT INTO assessments.ap2_topic_exam_occurrences
    (topic_id, exam_term, bereich, aufgabe_nummer, points, notes)
SELECT t.topic_id, v.exam_term, v.bereich, v.aufgabe_nummer, v.points, v.notes
FROM (VALUES
    -- ===== S2022 PB2 (=90P) =====
    ('projektmanagement',     'S2022', 'PB2', '1',   20, 'Projektplanung/Netzplan/kritischer Pfad'),
    ('vlan',                  'S2022', 'PB2', '2.a', 12, 'VLAN-Konfiguration'),
    ('ipv4-subnetting',       'S2022', 'PB2', '2.b', 13, 'IPv4 Subnetting'),
    ('ipv6-subnetting',       'S2022', 'PB2', '2.c', 10, 'IPv6 Anteil'),
    ('dmz-firewall',          'S2022', 'PB2', '2.d',  8, 'DMZ in Schulnetz-Aufgabe'),
    ('wlan',                  'S2022', 'PB2', '2.e',  7, 'WLAN-Anteil'),
    ('sql-queries',           'S2022', 'PB2', '3',   20, 'UPDATE/COUNT/ORDER BY/JOIN'),
    -- ===== S2022 PB3 (=90P) =====
    ('ipv4-subnetting',       'S2022', 'PB3', '1.a', 10, 'Routingtabelle + CIDR'),
    ('ipv6-subnetting',       'S2022', 'PB3', '1.b', 12, 'IPv6 Dual-Stack'),
    ('vpn-verschluesselung',  'S2022', 'PB3', '1.c', 16, 'VPN-Arten + IPsec Tunnel/Transport'),
    ('wlan',                  'S2022', 'PB3', '1.d', 12, 'WLAN 2,4/5GHz + WPA3'),
    ('er-modell',             'S2022', 'PB3', '2.a', 14, 'ERM n:m + Datentyp-Analyse'),
    ('sql-queries',           'S2022', 'PB3', '2.b',  6, 'SQL CREATE'),
    ('epk',                   'S2022', 'PB3', '3',   20, 'EPK lesen + EPK selbst erstellen'),
    -- ===== W2022/23 PB2 (=90P) =====
    ('iot-cps',               'W2022', 'PB2', '1',   32, 'IoT/CPS + LP-WAN + Gesundheitsdaten-DSGVO'),
    ('dmz-firewall',          'W2022', 'PB2', '2.a',  6, 'DMZ-Anteil'),
    ('vpn-verschluesselung',  'W2022', 'PB2', '2.b', 20, 'VPN + Verschlüsselung sym/asym/hybrid'),
    ('projektmanagement',     'W2022', 'PB2', '3.a', 12, 'Wasserfall vs Scrum'),
    ('er-modell',             'W2022', 'PB2', '3.b', 10, 'UML-Klassendiagramm (≈ ER)'),
    ('projektmanagement',     'W2022', 'PB2', '4',   10, 'Projektmerkmale + TCO/ROI'),
    -- ===== W2022/23 PB3 (=90P) =====
    ('ipv4-subnetting',       'W2022', 'PB3', '1.a', 10, 'Subnetting /17→/19'),
    ('ipv6-subnetting',       'W2022', 'PB3', '1.b',  6, 'IPv6 aus MAC EUI-64'),
    ('vlan',                  'W2022', 'PB3', '1.c',  8, 'VLAN+ARP+STP'),
    ('usv',                   'W2022', 'PB3', '1.d',  8, 'USV Überbrückungszeit-Berechnung'),
    ('netzwerkanalyse',       'W2022', 'PB3', '1.e', 19, 'DHCP/ARP/STP — Netzwerk-Diagnose'),
    ('epk',                   'W2022', 'PB3', '2.a', 15, 'EPK Rechnungsprüfung'),
    ('zuschlagskalkulation',  'W2022', 'PB3', '2.b',  6, 'Just-in-Time-Anteil'),
    ('sql-queries',           'W2022', 'PB3', '3.a', 10, 'NoSQL vs SQL Vergleich'),
    ('code-analyse',          'W2022', 'PB3', '3.b',  8, 'Python-Code analysieren'),
    -- ===== S2023 PB2 (=90P) =====
    ('netzwerkanalyse',       'S2023', 'PB2', '1.a', 15, 'Schulnetz Hardware-Auswahl'),
    ('wlan',                  'S2023', 'PB2', '1.b', 18, 'AP-Auswahl + 2,4/5GHz'),
    ('ipv4-subnetting',       'S2023', 'PB2', '1.c', 15, 'Subnetting 5 Netze'),
    ('dmz-firewall',          'S2023', 'PB2', '1.d',  4, 'DMZ-Anteil'),
    ('vpn-verschluesselung',  'S2023', 'PB2', '1.e', 11, 'AAA + Verschlüsselung'),
    ('vpn-verschluesselung',  'S2023', 'PB2', '2',   13, '2FA + Home-Office + DSGVO'),
    ('er-modell',             'S2023', 'PB2', '3',    6, 'CSV → ERM Entität ableiten'),
    ('projektmanagement',     'S2023', 'PB2', '4',    8, 'Projektplanung + Personalplanung'),
    -- ===== S2023 PB3 (=90P) =====
    ('virtualisierung',       'S2023', 'PB3', '1.a', 15, 'Hypervisor + VM'),
    ('schutzbedarf-bsi',      'S2023', 'PB3', '1.b', 24, 'Schutzbedarf BSI + CIA-Triade'),
    ('vlan',                  'S2023', 'PB3', '1.c', 20, 'VLAN-Anzahl 802.1Q'),
    ('er-modell',             'S2023', 'PB3', '2',   12, 'ERM Zeiterfassung 4 Tabellen'),
    ('projektmanagement',     'S2023', 'PB3', '3',    9, 'Agiles PM/Kanban'),
    ('snmp-monitoring',       'S2023', 'PB3', '4',   10, 'Fernverwaltung + SNMP-Monitoring'),
    -- ===== W2023/24 PB2 (=90P) =====
    ('osi-troubleshooting',   'W2023', 'PB2', '1.a',  4, 'OSI-Zuordnung'),
    ('netzwerkanalyse',       'W2023', 'PB2', '1.b',  5, 'Datenmenge + Routing'),
    ('vpn-verschluesselung',  'W2023', 'PB2', '1.c', 10, 'VPN Authentizität/Integrität/Vertraulichkeit'),
    ('ipv4-subnetting',       'W2023', 'PB2', '1.d', 16, 'Subnetting 8 PV-Standorte VLSM'),
    ('netzwerkanalyse',       'W2023', 'PB2', '1.e',  5, 'LWL/Übertragungstechnik'),
    ('er-modell',             'W2023', 'PB2', '2.a', 18, 'ER-Modell + Normalisierung'),
    ('sql-queries',           'W2023', 'PB2', '2.b', 10, 'SQL CREATE + SELECT AVG'),
    ('rechtsformen',          'W2023', 'PB2', '3.a',  8, 'Rechtsformen EU vs GmbH'),
    ('organigramm',           'W2023', 'PB2', '3.b',  8, 'Organigramm + Stablinie'),
    ('vollmachten',           'W2023', 'PB2', '3.c',  6, 'Prokura ppa. vs Handlungsvollmacht i.V.'),
    -- ===== W2023/24 PB3 (=90P) =====
    ('zuschlagskalkulation',  'W2023', 'PB3', '1.a', 12, 'Zuschlagskalkulation MEK→Brutto-VKP mit 7%% MwSt'),
    ('kaufvertrag',           'W2023', 'PB3', '1.b',  4, 'Kaufvertrag-Ablauf, 2 Willenserklärungen'),
    ('ipv4-subnetting',       'W2023', 'PB3', '2.a',  8, 'Subnetting /29 für DMZ'),
    ('dmz-firewall',          'W2023', 'PB3', '2.b',  8, 'Zweistufiges Firewall-Konzept'),
    ('mqtt',                  'W2023', 'PB3', '2.c',  6, 'MQTT-Broker'),
    ('netzwerkanalyse',       'W2023', 'PB3', '2.d',  4, 'Web-Proxy'),
    ('vlan',                  'W2023', 'PB3', '3.a',  8, 'VLAN Mgmt/Voice'),
    ('ipv4-subnetting',       'W2023', 'PB3', '3.b',  8, 'IPv4 Subnetting /25'),
    ('ipv6-subnetting',       'W2023', 'PB3', '3.c',  6, 'IPv6 aus ip-address-Output'),
    ('sql-queries',           'W2023', 'PB3', '4.a',  6, 'DBMS vs CSV Vorteile'),
    ('code-analyse',          'W2023', 'PB3', '4.b', 20, 'UML-Aktivitätsdiagramm/PAP'),
    -- ===== S2024 PB2 (=90P) =====
    ('rechtsformen',          'S2024', 'PB2', '1.a',  6, 'GmbH-Merkmale'),
    ('epk',                   'S2024', 'PB2', '1.b', 14, 'EPK Sozialauswahl mit XOR'),
    ('vpn-verschluesselung',  'S2024', 'PB2', '2.a', 13, 'IPsec-Paket-Analyse'),
    ('vlan',                  'S2024', 'PB2', '2.b',  5, 'VLAN-Typen Voice/Mgmt/Default'),
    ('nutzwertanalyse',       'S2024', 'PB2', '2.c', 13, 'Cloud vs On-Premise'),
    ('sql-queries',           'S2024', 'PB2', '3',   18, 'SQL UPDATE/DELETE mit Subquery'),
    ('iot-cps',               'S2024', 'PB2', '4.a', 13, 'CPS/IoT Sensoren/Aktoren/Edge'),
    ('osi-troubleshooting',   'S2024', 'PB2', '4.b',  8, 'OSI-Protokolle in IoT'),
    -- ===== S2024 PB3 (=90P) =====
    ('projektmanagement',     'S2024', 'PB3', '1',   22, 'Projektphasen + agile + Risikomanagement'),
    ('netzwerkanalyse',       'S2024', 'PB3', '2.a', 14, '3-Layer Core/Distribution/Access + Protokolle'),
    ('osi-troubleshooting',   'S2024', 'PB3', '2.b', 10, 'Bottom-Up OSI-Troubleshooting'),
    ('snmp-monitoring',       'S2024', 'PB3', '2.c', 14, 'SNMPv3 vs v2 + SSH/HTTPS + Verfügbarkeit'),
    ('mqtt',                  'S2024', 'PB3', '2.d', 10, 'MQTT bzw. Verfügbarkeit'),
    ('code-analyse',          'S2024', 'PB3', '3',   20, 'Pseudocode/Struktogramm Passwort + ASCII')
) AS v(slug, exam_term, bereich, aufgabe_nummer, points, notes)
JOIN topic_lookup t ON t.slug = v.slug
ON CONFLICT (topic_id, exam_term, aufgabe_nummer) DO UPDATE SET
    points = EXCLUDED.points,
    notes  = EXCLUDED.notes;

-- ---------------------------------------------------------------------------
-- 4. ZWEI WEITERE COMPUTE-FUNKTIONEN
-- ---------------------------------------------------------------------------

-- Wenn das Thema in einer Prüfung dran kommt: erwartete Punktzahl =
-- SUMME aller Occurrence-Punkte / ANZAHL eindeutiger Termine in denen es vorkam
CREATE OR REPLACE FUNCTION assessments.compute_ap2_topic_expected_points(p_topic_id UUID)
RETURNS NUMERIC AS $$
    SELECT ROUND(
        COALESCE(SUM(points)::NUMERIC / NULLIF(COUNT(DISTINCT exam_term), 0), 0),
        1
    )
    FROM assessments.ap2_topic_exam_occurrences
    WHERE topic_id = p_topic_id;
$$ LANGUAGE sql STABLE;

COMMENT ON FUNCTION assessments.compute_ap2_topic_expected_points IS
    'Erwartete Punktzahl für dieses Thema, WENN es in einer Prüfung vorkommt. '
    'Berechnung: SUM(points) / COUNT(DISTINCT termine wo Topic vorkam).';

-- Wie oft das Thema in den 5 analysierten Terminen vorkam (1-5)
CREATE OR REPLACE FUNCTION assessments.compute_ap2_topic_exam_count(p_topic_id UUID)
RETURNS INT AS $$
    SELECT COALESCE(COUNT(DISTINCT exam_term)::INT, 0)
    FROM assessments.ap2_topic_exam_occurrences
    WHERE topic_id = p_topic_id;
$$ LANGUAGE sql STABLE;

COMMENT ON FUNCTION assessments.compute_ap2_topic_exam_count IS
    'Anzahl der eindeutigen Prüfungstermine in denen das Thema vorkam (max 5 für 2022-2024).';

-- ---------------------------------------------------------------------------
-- 5. RECOMPUTE — alle drei Aggregate (bereich + expected_points + exam_count)
-- ---------------------------------------------------------------------------

UPDATE assessments.ap2_topics t
SET
    bereich = assessments.compute_ap2_topic_bereich(t.topic_id),
    expected_points = assessments.compute_ap2_topic_expected_points(t.topic_id),
    exam_count = assessments.compute_ap2_topic_exam_count(t.topic_id)
WHERE EXISTS (
    SELECT 1 FROM assessments.ap2_topic_exam_occurrences o
    WHERE o.topic_id = t.topic_id
);
