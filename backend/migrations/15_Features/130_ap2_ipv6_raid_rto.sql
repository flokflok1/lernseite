-- ============================================================================
-- Migration: 130_ap2_ipv6_raid_rto.sql
-- Description: 3 Themen massiv ausbauen basierend auf AP1-2026-BW + Dozenten-
--              Screenshots (105643 EUI-64, 113901 Subnetting, 115209 RTO/RPO):
--              — IPv6 EUI-64-Algorithmus (U/L-Bit-Flip, FFFE einschieben)
--              — IPv6-Subnetting aus /56 und /48 Präfixen
--              — RAID 5 vs 10 Berechnungen mit Striping-über-Mirrors
--              — "RAID ersetzt kein Backup" mit 4+ Argumenten
--              — 3-2-1-Regel + Verfügbarkeitsklassen
--              — NEU: Disaster Recovery (RTO/RPO) als eigenes Topic
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-04-18
-- ============================================================================

-- ============================================================================
-- Teil 1: Neues Topic "Disaster Recovery (RTO/RPO)" anlegen
-- ============================================================================
INSERT INTO assessments.ap2_topics
    (slug, name_de, name_en, bereich, priority, expected_points, description)
VALUES
('disaster-recovery',
 'Disaster Recovery (RTO/RPO)',
 'Disaster Recovery (RTO/RPO)',
 'both',
 'sehr-hoch',
 8,
 'Notfallwiederherstellung: RTO (Recovery Time Objective) und RPO (Recovery Point Objective) als SLA-Zielvorgaben. Screenshot 115209 zeigt: der BW-Dozent prüft das explizit in Verbindung mit RAID/Backup-Aufgaben. AP1-2026-BW hatte 4P dafür.')
ON CONFLICT (slug) DO UPDATE
SET priority = 'sehr-hoch', expected_points = 8;

-- Auch Topics "raid-backup" sicherstellen (existiert möglicherweise schon als Teil anderer)
INSERT INTO assessments.ap2_topics
    (slug, name_de, name_en, bereich, priority, expected_points, description)
VALUES
('raid-backup',
 'RAID & Backup-Konzepte',
 'RAID & Backup Concepts',
 'both',
 'sehr-hoch',
 15,
 'RAID-Level (0/1/5/6/10) mit Berechnungsformeln für nutzbare Kapazität, "RAID ersetzt kein Backup", 3-2-1-Regel, GFS-Generationenprinzip, Verfügbarkeitsklassen. AP1-2026-BW: 15P auf IT3. Klassiker in BW-Prüfungen.')
ON CONFLICT (slug) DO UPDATE
SET priority = 'sehr-hoch', expected_points = 15;

-- ============================================================================
-- Teil 2: Learning Items
-- ============================================================================

WITH topic_lookup AS (
    SELECT slug, topic_id FROM assessments.ap2_topics
)
INSERT INTO assessments.ap2_learning_items
    (topic_id, item_type, prompt, model_answer, expected_answer_structure,
     grading_criteria, points, source_exam, difficulty, estimated_time_sec)
SELECT t.topic_id, v.item_type, v.prompt, v.model_answer,
       v.expected_answer_structure::jsonb,
       v.grading_criteria::jsonb,
       v.points, v.source_exam, v.difficulty, v.estimated_time_sec
FROM (VALUES

-- ============================================================
-- IPv6 — EUI-64-Algorithmus (Screenshot 105643)
-- ============================================================

('ipv6-subnetting', 'application',
 'Die Netzwerkkarte eines Admin-PCs hat die MAC-Adresse DC:56:7B:F8:89:13. Bilden Sie die Link-Local-IPv6-Adresse des PCs nach dem EUI-64-Verfahren. Zeigen Sie alle drei Schritte.',
 'Schritt 1 — MAC-Adresse in 8-Bit-Blöcken notieren:
DC : 56 : 7B : F8 : 89 : 13  (48 Bit / 6 Oktette)

Schritt 2 — FFFE in die Mitte einfügen (zwischen 3. und 4. Oktett):
DC : 56 : 7B : FF : FE : F8 : 89 : 13  (64 Bit / 8 Oktette)

Schritt 3 — U/L-Bit invertieren (das 7. Bit des 1. Oktetts):
DC in binär: 1101 1100
                   ^ das 7. Bit (U/L) ist 0
Invertieren auf 1: 1101 1110 = DE
Ergebnis: DE : 56 : 7B : FF : FE : F8 : 89 : 13

Schritt 4 — Präfix fe80::/10 voranstellen und in IPv6-Notation umwandeln (Gruppen zu 16 Bit):
fe80 : 0000 : 0000 : 0000 : de56 : 7bff : fef8 : 8913

Schritt 5 — Kurzform mit :: (zusammenhängende Null-Gruppen weglassen):
fe80::de56:7bff:fef8:8913/64

ACHTUNG: U/L-Bit-Flip ist DER Fallstrick. Es wird das ZWEIT-niederwertigste Bit (= 7. Bit von links) des 1. Oktetts umgedreht. Wer es vergisst, bekommt 0 Punkte.',
 '{"required_concepts": ["Schritt 1 MAC notieren", "Schritt 2 FFFE einfügen Mitte", "Schritt 3 7. Bit invertieren U/L-Bit", "DC zu DE", "fe80 Präfix", "Kurzform fe80::de56:7bff:fef8:8913", "64 Bit Interface-ID"]}',
 '[{"criterion": "FFFE korrekt eingefügt", "weight": 2, "description": "zwischen 3. und 4. Oktett", "required": true},
   {"criterion": "U/L-Bit invertiert", "weight": 3, "description": "DC zu DE", "required": true},
   {"criterion": "fe80:: Präfix", "weight": 2, "description": "Link-Local-Kennung", "required": true},
   {"criterion": "Kurzform korrekt", "weight": 2, "description": ":: für Nullen", "required": true},
   {"criterion": "/64 Präfixlänge", "weight": 1, "description": "Interface-ID ist 64 Bit", "required": false}]',
 8, 'W2026-BW-Lindner-EUI64', 5, 900),

-- IPv6-Subnetting-Aufgabe analog AP1-2026-BW (3.4)
('ipv6-subnetting', 'application',
 'Ihr Provider hat der Firma „Agrarenergie Müller e. K." das IPv6-Präfix 2001:0db8:00ea:2300::/56 zugewiesen. Sie sollen folgende Subnetze einrichten:
- /64 für Verwaltungs-LAN
- /64 für WLAN
- /64 für Server-DMZ

a) Wie viele /64-Subnetze kann man insgesamt aus dem /56 bilden? Rechnen Sie das in Zweierpotenz.
b) Geben Sie die ersten drei /64-Subnetze als konkrete IPv6-Präfixe an.
c) Der Admin-PC mit der internen Nummer AB.1001 soll die globale IPv6 des ersten Subnetzes erhalten. Bilden Sie seine IP (Kurzform) mit der Interface-ID ab10:01. Geben Sie außerdem Default-Gateway und DNS-Server an, wenn der Router Link-Local fe80::1 und der DNS-Server Link-Local fe80::d hat.',
 'a) Verfügbare Bits für Subnetting: 64 - 56 = 8 Bit.
Anzahl möglicher /64-Subnetze: 2^8 = 256.

b) Die ersten drei /64-Subnetze (Subnetz-Teil in den Bits 57-64 durchzählen):
- Subnetz 1 (Verwaltung): 2001:db8:ea:2300::/64
- Subnetz 2 (WLAN):       2001:db8:ea:2301::/64
- Subnetz 3 (Server-DMZ): 2001:db8:ea:2302::/64

(Weitere bis 2001:db8:ea:23ff::/64 für Subnetz 256.)

c) Admin-PC AB.1001 im Verwaltungs-Subnetz (/64 Nr. 1) mit Interface-ID ab10:01:
Globale IPv6: 2001:db8:ea:2300::ab10:01/64 (Kurzform — alle Nullen in Interface-ID als :: weglassbar)
Alternativ als Langform: 2001:0db8:00ea:2300:0000:0000:ab10:0001/64

Default-Gateway: fe80::1 (Link-Local des Routers — IPv6-Standard)
DNS-Server: fe80::d

Anmerkung: Link-Local-Adressen werden bei IPv6 bevorzugt für Gateway und DNS genutzt, da sie unabhängig von Subnetz-Änderungen stabil bleiben. Alternative globale Variante wäre 2001:db8:ea:2300::1 (Gateway) und ::d (DNS).',
 '{"required_concepts": ["2^8 = 256 Subnetze", "Subnetze 2300, 2301, 2302", "Admin-PC 2001:db8:ea:2300::ab10:01/64", "Kurzform ::", "Gateway fe80::1 Link-Local", "DNS fe80::d"]}',
 '[{"criterion": "Bit-Rechnung korrekt", "weight": 2, "description": "64-56=8, 2^8=256", "required": true},
   {"criterion": "3 Subnetze durchnummeriert", "weight": 3, "description": "2300/2301/2302", "required": true},
   {"criterion": "Admin-PC IPv6 Kurzform", "weight": 3, "description": "::ab10:01/64", "required": true},
   {"criterion": "Gateway/DNS Link-Local", "weight": 2, "description": "fe80::1, fe80::d", "required": true},
   {"criterion": "Kurzform-Regel begründet", "weight": 1, "description": ":: ersetzt zusammenhängende Nullen", "required": false}]',
 10, 'W2026-BW-AP1-Pattern-IPv6', 4, 1200),

-- ============================================================
-- RAID — Kapazitätsberechnungen + Kernargumente
-- ============================================================

('raid-backup', 'application',
 'Die „Schnellinger GmbH" plant ein neues Storage-Array mit 8 Festplatten à 4 TB (keine Hot-Spare). Der Admin soll RAID 5, RAID 6 und RAID 10 vergleichen.

a) Berechnen Sie die nutzbare Kapazität für alle drei RAID-Level.
b) Wie viele Plattenausfälle verträgt jedes Level maximal?
c) Welches Level empfehlen Sie für eine Datenbank mit hoher Schreiblast und warum?',
 'a) Kapazitätsberechnungen (n Platten × Größe):
- RAID 5 (1 Paritätsplatte): (n-1) × Größe = (8-1) × 4 TB = 7 × 4 = 28 TB
- RAID 6 (2 Paritätsplatten): (n-2) × Größe = (8-2) × 4 TB = 6 × 4 = 24 TB
- RAID 10 (Striping über Mirrors): (n/2) × Größe = (8/2) × 4 TB = 4 × 4 = 16 TB

b) Ausfalltoleranz:
- RAID 5: genau 1 Platte. Zweiter Ausfall = Datenverlust.
- RAID 6: genau 2 Platten.
- RAID 10: 1 bis 4 Platten — abhängig davon, ob die Ausfälle auf verschiedene Mirror-Paare verteilt sind. Max 4 Platten (jeweils eine pro Mirror-Paar).

c) Empfehlung für Datenbank mit hoher Schreiblast: RAID 10.
Begründung:
1. Kein Parity-Overhead → jeder Schreibzugriff geht an 2 Platten (Spiegelung), statt an Parity-Neuberechnung — deutlich schneller.
2. RAID 5 hat die "Write Penalty" (4 IOs pro logischem Schreibzugriff: 2 Read + 2 Write für Parity-Update).
3. Bei Plattenausfall kein Rebuild aus Parität — Mirror-Partner übernimmt sofort, keine Performance-Einbußen.
4. Schneller Rebuild (nur Mirror kopieren, keine Parity berechnen).
Nachteil: 50 % Kapazitätsverlust gegenüber RAID 5.

Bei reiner Archivlast (viel Lesen, selten Schreiben) wäre RAID 6 wirtschaftlicher.',
 '{"required_concepts": ["RAID 5 28 TB", "RAID 6 24 TB", "RAID 10 16 TB", "RAID 5 1 Platte", "RAID 6 2 Platten", "RAID 10 bis 4 Platten verteilt", "Write Penalty", "RAID 10 für Datenbank", "50% Verlust"]}',
 '[{"criterion": "3 Kapazitäten korrekt", "weight": 3, "description": "28/24/16 TB", "required": true},
   {"criterion": "Ausfalltoleranz korrekt", "weight": 2, "description": "1/2/bis-4", "required": true},
   {"criterion": "RAID 10 für Datenbank empfohlen", "weight": 2, "description": "mit Begründung", "required": true},
   {"criterion": "Write Penalty erwähnt", "weight": 2, "description": "RAID 5 Parity-Overhead", "required": true},
   {"criterion": "Kapazitätstrade-off erwähnt", "weight": 1, "description": "50% Verlust", "required": false}]',
 10, 'W2026-BW-AP1-Pattern-RAID', 4, 1200),

('raid-backup', 'cued',
 'Erläutern Sie die Aussage „RAID ersetzt kein Backup" mit mindestens vier konkreten Argumenten.',
 'RAID schützt nur vor HARDWARE-Ausfall einzelner Platten. Folgende Szenarien kann RAID NICHT abfangen:

1. Versehentliches Löschen oder Überschreiben von Dateien durch Nutzer oder fehlerhafte Skripte.
   → Die Löschung wird auf allen Mirrors/durch Parität weitergegeben — Daten unwiderruflich weg.

2. Ransomware / Viren / Malware.
   → Verschlüsselt Dateien, schreibt das auf alle Spiegel. RAID schützt nicht vor "bösem" Schreibzugriff.

3. Datenbank-Korruption durch Software-Bug oder fehlerhaftes Update.
   → Korrupte Datenbank wird identisch auf alle Platten gespiegelt.

4. Katastrophen am Standort: Brand, Hochwasser, Diebstahl, Blitzschlag.
   → Alle Platten sind im selben Gehäuse am selben Ort.

5. Bit-Rot / stillschweigende Datenkorruption durch defekten RAID-Controller.
   → RAID bemerkt es nicht, falsche Daten werden auf alle Platten verteilt.

6. Menschliche Fehler in Administration (fehlerhafte Migrationen, versehentliches Formatieren).

Fazit: RAID schützt vor *Hardware-Defekt*, Backup schützt vor *Datenverlust durch Software-, Bedien- oder Katastrophenfehler*. Beides ist notwendig und ergänzt sich.

Backup-Konzept nach dem 3-2-1-Prinzip:
- 3 Kopien der Daten (Original + 2 Backups),
- auf 2 unterschiedlichen Medientypen (z.B. HDD + LTO-Tape, oder HDD + Cloud),
- 1 Kopie an einem externen Standort (Off-Site, z.B. Cloud, Brandschutztresor oder zweites Rechenzentrum).',
 '{"required_concepts": ["versehentlich löschen", "Ransomware Malware", "Datenbank-Korruption", "Katastrophe Brand Diebstahl", "Bit-Rot Controller-Defekt", "menschlicher Fehler", "3-2-1-Regel 3 Kopien 2 Medien 1 extern"]}',
 NULL, 8, 'W2026-BW-AP1-Pattern-RAID', 3, 480),

('raid-backup', 'cued',
 'Erklären Sie das Generationenprinzip (GFS = Grandfather-Father-Son) beim Backup und nennen Sie eine konkrete Rotationsstrategie.',
 'GFS-Prinzip (Grandfather-Father-Son) ist eine gestaffelte Backup-Rotation mit drei Ebenen:

- Son (Sohn): Tägliches Backup, meist inkrementell oder differenziell. Enthält nur die Änderungen seit dem letzten Backup.
- Father (Vater): Wöchentliches Backup, meist differenziell oder voll. Enthält alle Änderungen seit letztem Vollbackup.
- Grandfather (Großvater): Monatliches Vollbackup, dauerhaft archiviert.

Typische Rotation:
- Son: Mo/Di/Mi/Do inkrementell (→ 4 Medien rotiert).
- Father: Fr wöchentliches Voll- oder Differenzbackup (→ 4 Medien pro Monat).
- Grandfather: letztes Freitagsbackup im Monat als Vollsicherung archivieren (→ 12+ Medien pro Jahr).

Retention (Aufbewahrung): Sohn 1 Woche, Vater 1 Monat, Großvater 1 Jahr oder länger (abhängig von gesetzlichen Aufbewahrungsfristen — HGB: 10 Jahre für Steuerunterlagen).

Vorteil: Kombiniert kurze Wiederherstellungszeit bei aktuellen Fehlern (Son) mit langfristiger Historie (Grandfather).

Zusatzbegriffe:
- Vollbackup: Alle Daten. Groß, langsam, aber eigenständig wiederherstellbar.
- Differenziell: Alle Änderungen seit dem letzten Vollbackup. Mittelgroß.
- Inkrementell: Änderungen seit dem letzten Backup (egal welchen Typ). Klein, schnell, aber Wiederherstellung braucht alle inkrementellen Backups der Kette.',
 '{"required_concepts": ["Son täglich inkrementell", "Father wöchentlich", "Grandfather monatlich Vollbackup", "Retention 1 Woche / 1 Monat / 1 Jahr", "inkrementell vs differenziell vs voll", "HGB-Aufbewahrung 10 Jahre"]}',
 NULL, 5, 'ki-generated', 3, 300),

-- ============================================================
-- Verfügbarkeitsklassen
-- ============================================================

('raid-backup', 'cued',
 'Berechnen Sie die maximale tolerierbare Ausfallzeit pro Jahr für die Verfügbarkeitsklassen 3 (99,9 %), 4 (99,99 %) und 5 (99,999 %). Welche technischen Maßnahmen sind für Klasse 5 notwendig?',
 'Jahr in Minuten: 365 × 24 × 60 = 525.600 min.

Klasse 3 (99,9 % = 99,9/100 verfügbar):
Ausfall = 0,1 % × 525.600 = 525,6 min ≈ 8,76 Stunden/Jahr.

Klasse 4 (99,99 %):
Ausfall = 0,01 % × 525.600 = 52,56 min/Jahr (≈ 53 Minuten).

Klasse 5 (99,999 % = "five nines"):
Ausfall = 0,001 % × 525.600 = 5,256 min/Jahr (≈ 5 Minuten).

Technische Maßnahmen für Klasse 5:
1. Redundante Hardware: Zwei Netzteile, doppelte Mainboards, Hot-Swap überall.
2. Cluster / Failover: Aktive + passive Server automatisch umschalten (Pacemaker, VMware HA).
3. Georedundanz: zweites RZ am anderen Standort mit Synchroner Replikation.
4. Load Balancer / Anycast-DNS vor mehreren Servern.
5. Redundante Netzwerkanbindung (2 verschiedene Provider, BGP-Failover).
6. USV + Notstromdiesel.
7. Monitoring + On-Call-Team 24/7 (max. 5 min Downtime = keine Zeit für manuellen Eingriff).
8. Testing: Regelmäßige Disaster-Recovery-Drills.

Klasse 5 bedeutet in der Praxis: Lösungen müssen beim Betrieb nahtlos weiterlaufen können, ohne dass ein Einzelausfall zu Downtime führt.',
 '{"required_concepts": ["525.600 min pro Jahr", "Klasse 3 525 min 8,76h", "Klasse 4 52 min", "Klasse 5 5 min five nines", "Redundanz Hardware", "Cluster Failover HA", "Georedundanz", "USV Notstromdiesel", "24/7 Monitoring"]}',
 NULL, 6, 'ki-generated', 4, 480),

-- ============================================================
-- RTO/RPO (Screenshot 115209 — explizit prüfungsrelevant)
-- ============================================================

('disaster-recovery', 'cued',
 'Die Firma „Schnellinger GmbH" definiert in ihren Service Level Agreements zwei Notfall-Zielvorgaben: RTO (Recovery Time Objective) und RPO (Recovery Point Objective). Erläutern Sie beide Begriffe und geben Sie ein konkretes Beispiel.',
 'RTO (Recovery Time Objective) — Wiederanlaufzeit:
Die maximal tolerierbare Zeitspanne zwischen dem Eintreten des Ausfalls und dem vollständigen Wiederanlauf des Systems.
Beispiel: RTO = 30 Minuten — der Webshop muss spätestens 30 Minuten nach dem Datenbank-Crash wieder erreichbar sein.
Einflussfaktoren: Backup-Restore-Zeit, Hardware-Austausch-Dauer, manuelle Eingriffe. Kürzere RTO erfordert automatisches Failover, Cluster, Hot-Spare-Systeme.

RPO (Recovery Point Objective) — Datenverlust-Toleranz:
Die maximal tolerierbare Datenmenge (gemessen in Zeit seit letzter Sicherung), die im Notfall verloren gehen darf.
Beispiel: RPO = 15 Minuten — es darf höchstens das letzte Viertelstunden-Intervall an Transaktionen verloren gehen. Technische Konsequenz: Backups/Snapshots mindestens alle 15 Minuten, oder synchrone Replikation.

Merkregel: RTO misst ZEIT (wie lange dauert die Wiederherstellung), RPO misst DATEN (wie viel Datenverlust ist okay).

Zusammenhang mit anderen SLA-Kennzahlen:
- MTTR (Mean Time To Repair): durchschnittliche tatsächliche Reparaturzeit — muss unter RTO bleiben.
- MTBF (Mean Time Between Failures): durchschnittliche Zeit zwischen Ausfällen.
- BIA (Business Impact Analysis): identifiziert kritische Geschäftsprozesse und liefert RTO/RPO-Vorgaben.',
 '{"required_concepts": ["RTO Recovery Time Objective", "RPO Recovery Point Objective", "RTO Zeit bis Wiederanlauf", "RPO maximaler Datenverlust", "Beispiel RTO 30 min / RPO 15 min", "synchrone Replikation für niedrige RPO", "Cluster Failover für niedrige RTO", "MTTR MTBF BIA"]}',
 NULL, 6, 'W2026-BW-Lindner-RTO', 4, 420),

('disaster-recovery', 'application',
 'Für den Online-Shop der „Agrarenergie Müller e. K." werden folgende SLA-Werte gefordert: RTO = 2 Stunden, RPO = 15 Minuten, Verfügbarkeit 99,95 %. Beschreiben Sie ein technisches und organisatorisches Konzept, das diese Vorgaben erfüllen kann. Gehen Sie auf: Backup-Strategie, Hochverfügbarkeit, Monitoring, Rollen.',
 'Backup-Strategie (für RPO = 15 min):
- Alle 15 min: Inkrementelles Backup der Datenbank (Binlog-Shipping oder WAL-Streaming bei PostgreSQL).
- Alle 4 h: Differenzielles Backup.
- Täglich 02:00 Uhr: Vollbackup, gesichert auf separatem Storage.
- 3-2-1-Prinzip: 3 Kopien, 2 Medientypen (lokales NAS + LTO-Tape), 1 Kopie off-site in Cloud (AWS S3 Glacier).

Hochverfügbarkeit (für RTO = 2h, Verfügbarkeit 99,95 % = max. 4,38 h Downtime/Jahr):
- Web-/Applikationsserver: 2 identische Server hinter Load Balancer (aktiv-aktiv). Ausfall eines Servers = keine Downtime.
- Datenbankserver: Primary-Replica mit synchroner Replikation. Bei Primary-Ausfall automatisches Failover auf Replica.
- Redundante Netzteile, redundante Netzwerkanbindung (2 Provider, DNS-Failover).
- USV + Notstromdiesel für 24h Überbrückung.

Monitoring (für schnelle Reaktion):
- Icinga/Zabbix/Grafana: 24/7 Überwachung aller Komponenten.
- Alerting via SMS + Mail an Bereitschaft bei Schwellwerten (CPU > 90 %, Disk > 85 %, Ping-Timeout > 2 s).
- Automatische Failover-Skripte, die bei definierten Kriterien selbständig umschalten.

Rollen (für RTO-Kompatibilität):
- 24/7-Bereitschaft (2 Mitarbeiter rotieren pro Woche), max. 30 min Reaktionszeit.
- Runbook für häufigste Incidents (Failover, Rollback, Service-Restart).
- Monatliche Disaster-Recovery-Drills (Failover testen).

Rechtliche Dokumentation (BW-Klassiker):
- BIA (Business Impact Analysis) dokumentieren.
- DSGVO: Datenbackups verschlüsseln, Löschfristen einhalten.
- Notfallhandbuch nach BSI-Grundschutz.',
 '{"required_concepts": ["inkrementell alle 15 min für RPO", "3-2-1 Backup", "Load Balancer aktiv-aktiv", "DB Primary-Replica Failover", "synchrone Replikation", "USV Notstromdiesel", "Monitoring Alerting 24/7", "Runbook", "DR-Drill", "BIA", "DSGVO"]}',
 '[{"criterion": "Backup deckt RPO ab", "weight": 3, "description": "15 min Intervalle", "required": true},
   {"criterion": "HA deckt RTO ab", "weight": 3, "description": "Load Balancer + DB-Failover", "required": true},
   {"criterion": "Monitoring mit Alerting", "weight": 2, "description": "24/7 + Schwellwerte", "required": true},
   {"criterion": "Organisatorisch: Bereitschaft + Runbook", "weight": 2, "description": "RTO-konform", "required": true},
   {"criterion": "DR-Drills erwähnt", "weight": 1, "description": "regelmäßig", "required": false},
   {"criterion": "Rechtliches: BIA/DSGVO/BSI", "weight": 1, "description": "BW-Klassiker", "required": false}]',
 12, 'W2026-BW-Agrarenergie-DR-Konzept', 5, 1500)

) AS v(slug, item_type, prompt, model_answer,
       expected_answer_structure, grading_criteria, points, source_exam, difficulty, estimated_time_sec)
JOIN topic_lookup t ON t.slug = v.slug;

COMMIT;
