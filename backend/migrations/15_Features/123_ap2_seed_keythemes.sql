-- ============================================================================
-- Migration: 123_ap2_seed_keythemes.sql
-- Description: Seed für die 5 Schlüsselthemen (Phase 7 des AP2-Rebuilds).
--              Pro Topic: 2-3 Blurting-Prompts, 5-7 Cued-Fragen, 2-3 Application.
--              Themen: EPK, Subnetting, USV, OSI-Troubleshooting, Zuschlagskalkulation
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-04-18
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
-- 1. EPK (Ereignisgesteuerte Prozesskette)
-- ============================================================

('epk', 'blurt',
 'Schreibe alles auf was du über die EPK (ereignisgesteuerte Prozesskette) weißt: Symbole, Konnektoren (UND/ODER/XOR), Regeln, Notation, Erweiterungen mit Organisationseinheiten und Informationsobjekten.',
 'EPK-Bausteine: Ereignis (Sechseck/Hexagon, passiv, beschreibt Zustand), Funktion (abgerundetes Rechteck, aktiv, beschreibt Handlung), Konnektoren UND (∧) / ODER (∨) / XOR (×). Regel: Ereignis und Funktion müssen sich abwechseln. Konnektoren entscheiden den Verlauf nach einer Funktion oder fügen Pfade nach einem Ereignis zusammen. XOR = genau eine Verzweigung tritt ein. UND = alle parallel. ODER = mindestens eine. Erweiterungen: Organisationseinheiten (Ellipse, rechts an Funktion), Informationsobjekte (Rechteck mit Datenträger-Symbol). Start- und End-Ereignisse markieren Anfang/Ende des Prozesses.',
 '{"required_concepts": ["Ereignis", "Funktion", "Konnektor", "XOR", "UND", "ODER", "Start-Ereignis", "End-Ereignis", "Organisationseinheit", "Informationsobjekt", "Sechseck", "Rechteck"]}',
 '[{"criterion": "Bausteine benannt", "weight": 4, "description": "Ereignis/Funktion/Konnektor erklärt", "required": true},
   {"criterion": "Konnektor-Semantik", "weight": 4, "description": "XOR/UND/ODER korrekt unterschieden", "required": true},
   {"criterion": "Regeln", "weight": 2, "description": "Wechsel-Regel Ereignis/Funktion erwähnt", "required": false},
   {"criterion": "Erweiterungen", "weight": 2, "description": "Organisationseinheit + Informationsobjekt erwähnt", "required": false}]',
 14, 'ki-generated', 3, 600),

('epk', 'cued',
 'Was ist der Unterschied zwischen Ereignis und Funktion in einer EPK? Nenne auch das jeweilige Symbol.',
 'Ereignis = passiver Zustand (z.B. "Bestellung eingegangen"), Symbol: Sechseck/Hexagon. Funktion = aktive Handlung (z.B. "Bestellung prüfen"), Symbol: abgerundetes Rechteck. Sie wechseln sich in der EPK ab.',
 '{"required_concepts": ["Ereignis passiv", "Funktion aktiv", "Sechseck", "abgerundetes Rechteck"]}',
 NULL, 2, 'ki-generated', 2, 90),

('epk', 'cued',
 'Welche Konnektoren gibt es in der EPK und was bedeuten sie semantisch?',
 'UND (∧): alle Pfade laufen parallel. ODER (∨): mindestens ein Pfad — nicht ausschließend. XOR/exklusives ODER (×): genau ein Pfad — die Pfade schließen sich gegenseitig aus.',
 '{"required_concepts": ["UND parallel", "ODER mindestens eins", "XOR genau eins"]}',
 NULL, 3, 'ki-generated', 2, 90),

('epk', 'cued',
 'Nach einer Funktion "Kreditwürdigkeit prüfen" treten zwei Möglichkeiten ein: "Kunde kreditwürdig" ODER "Kunde nicht kreditwürdig". Welcher Konnektor verbindet die Funktion mit den Ereignissen?',
 'XOR (exklusives ODER) — denn nur eines der beiden Ereignisse tritt ein, sie schließen sich gegenseitig aus.',
 '{"required_concepts": ["XOR", "exklusiv", "schließt aus"]}',
 NULL, 2, 'ki-generated', 2, 60),

('epk', 'cued',
 'Wie ergänzt man Organisationseinheiten und Informationsobjekte in einer EPK? Wo werden sie platziert?',
 'Organisationseinheiten (Ellipse) werden RECHTS an die Funktion angehängt — sie zeigen WER die Funktion ausführt (z.B. "Vertrieb"). Informationsobjekte (Rechteck mit Datenträgersymbol) werden ebenfalls an die Funktion angehängt — sie zeigen WELCHE Daten verarbeitet werden (z.B. "Bestelldatensatz").',
 '{"required_concepts": ["Organisationseinheit Ellipse", "Informationsobjekt Rechteck", "an Funktion", "wer", "welche Daten"]}',
 NULL, 2, 'ki-generated', 3, 120),

('epk', 'cued',
 'Welche zwei Konnektoren sind nach einem Ereignis NICHT erlaubt und warum?',
 'XOR und ODER sind nach einem Ereignis NICHT erlaubt. Grund: ein Ereignis kann keine Entscheidung treffen — Entscheidungen werden NUR durch Funktionen getroffen. Nach einem Ereignis ist nur UND-Verzweigung sinnvoll (parallele Verarbeitung).',
 '{"required_concepts": ["XOR nicht nach Ereignis", "ODER nicht nach Ereignis", "Ereignis keine Entscheidung", "Funktion entscheidet"]}',
 NULL, 2, 'ki-generated', 4, 90),

('epk', 'application',
 'Erstelle eine EPK für den Geschäftsprozess Sozialauswahl bei Stellenabbau (vereinfachtes Szenario): Start "Personalabbau geplant" → Sozialauswahl durchführen → entweder Mitarbeiter wird übernommen ODER Mitarbeiter erhält Kündigung. Bei Übernahme: E-Mail an Mitarbeiter + Personalakte aktualisieren. Bei Kündigung: Einschreiben senden + Personalgespräch führen → Mitarbeiter mit Abfindung ausscheiden ODER Mitarbeiter wechselt auf reduzierte Stelle. Beschreibe die EPK textuell mit allen Ereignissen, Funktionen und Konnektoren.',
 'Start-Ereignis: "Personalabbau geplant" → Funktion: "Sozialauswahl durchführen" → XOR-Konnektor → Ereignisse: "Mitarbeiter wird übernommen" XOR "Mitarbeiter erhält Kündigung". \n\nBei Übernahme: → UND-Konnektor → parallele Funktionen "E-Mail versenden" + "Personalakte aktualisieren" → UND-Verbindung → End-Ereignis "Mitarbeiter im Unternehmen". \n\nBei Kündigung: → UND-Konnektor → Funktionen "Einschreiben senden" + "Personalgespräch führen" → UND-Verbindung → Ereignis "Gespräch geführt" → Funktion "Vertragsangebot machen" → XOR-Konnektor → Ereignisse "Mitarbeiter akzeptiert Abfindung" XOR "Mitarbeiter akzeptiert reduzierte Stelle" → End-Ereignisse.',
 '{"required_concepts": ["Start-Ereignis", "End-Ereignis", "XOR Verzweigung", "UND Parallelisierung", "Sozialauswahl Funktion", "korrekte Reihenfolge", "Mitarbeiter-Wege getrennt"]}',
 '[{"criterion": "Start/End-Ereignisse", "weight": 2, "description": "Korrekt markiert", "required": true},
   {"criterion": "XOR nach Sozialauswahl", "weight": 4, "description": "Verzweigung Übernehmen/Kündigen", "required": true},
   {"criterion": "UND für parallele Aktionen", "weight": 4, "description": "E-Mail + Personalakte parallel", "required": true},
   {"criterion": "Vollständigkeit Pfade", "weight": 4, "description": "Beide XOR-Pfade durchgespielt", "required": true}]',
 14, 'S2024-PB2-1.2', 4, 1200),

('epk', 'application',
 'Erstelle eine EPK für die Rechnungsprüfung (W2022 PB3 Aufg.2 vereinfacht): Start "Rechnung eingegangen" → Rechnung prüfen → Bei Übereinstimmung mit Bestellung: Rechnung freigeben + Buchungssatz erfassen + Zahlung anweisen. Bei Abweichung: Reklamation an Lieferant senden → bei Klärung positiv: zurück zur Rechnungsprüfung. Beschreibe die EPK strukturiert.',
 'Start: "Rechnung eingegangen" → Funktion "Rechnung mit Bestellung abgleichen" → XOR → "Rechnung stimmt mit Bestellung überein" XOR "Abweichung festgestellt". \n\nBei Übereinstimmung: → UND → Funktionen "Rechnung freigeben" + "Buchungssatz erfassen" + "Zahlung anweisen" → UND-Verbindung → End-Ereignis "Rechnung bezahlt". \n\nBei Abweichung: → Funktion "Reklamation an Lieferant senden" → Ereignis "Klärung läuft" → Funktion "Klärung abwarten" → XOR → "Klärung positiv" XOR "Klärung negativ". Bei positiv: zurück zur Rechnungsprüfung. Bei negativ: End-Ereignis "Rechnung abgelehnt".',
 '{"required_concepts": ["Rechnungsprüfung Funktion", "XOR Übereinstimmung/Abweichung", "UND parallele Buchungsschritte", "Rückführungsschleife bei Reklamation", "End-Ereignisse beide Pfade"]}',
 '[{"criterion": "XOR-Verzweigung", "weight": 4, "description": "Übereinstimmung vs Abweichung", "required": true},
   {"criterion": "Parallele Buchungsschritte", "weight": 4, "description": "UND für Freigabe/Buchung/Zahlung", "required": true},
   {"criterion": "Schleife bei Reklamation", "weight": 4, "description": "Zurück zur Rechnungsprüfung", "required": false},
   {"criterion": "Vollständigkeit", "weight": 3, "description": "Beide End-Pfade beschrieben", "required": true}]',
 15, 'W2022-PB3-2', 4, 1200),

-- ============================================================
-- 2. IPv4-Subnetting
-- ============================================================

('ipv4-subnetting', 'blurt',
 'Schreibe alles auf was du über IPv4-Subnetting weißt: CIDR-Notation, Subnetzmaske, Hostbits, Netz-/Broadcast-Adresse, VLSM, "lückenlos aufeinander folgende" Subnetze.',
 'IPv4-Adresse = 32 Bit, geteilt in Netz- und Hostbits durch Subnetzmaske. CIDR-Notation /n gibt Anzahl Netzbits an (z.B. /24 = 255.255.255.0). Hostanzahl = 2^(32-n) - 2 (Netz- und Broadcast-Adresse abziehen). Netz-Adresse: alle Hostbits = 0. Broadcast: alle Hostbits = 1. VLSM (Variable Length Subnet Masking) = Subnetze unterschiedlicher Größe innerhalb eines Adressbereichs. Vorgehen: Subnetze nach Hostanzahl absteigend sortieren, kleinste passende Maske wählen, lückenlos aneinanderreihen (wichtig in BW-Prüfungen!).',
 '{"required_concepts": ["32 Bit", "CIDR /n", "Subnetzmaske", "Hostbits 2^x - 2", "Netz-Adresse", "Broadcast-Adresse", "VLSM", "absteigend sortieren", "lückenlos"]}',
 '[{"criterion": "CIDR-Notation", "weight": 3, "description": "/n erklärt", "required": true},
   {"criterion": "Hostberechnung", "weight": 3, "description": "2^(32-n) - 2", "required": true},
   {"criterion": "Netz/Broadcast", "weight": 2, "description": "Erste/letzte Adresse", "required": true},
   {"criterion": "VLSM", "weight": 4, "description": "Lückenlos + sortieren", "required": true}]',
 12, 'ki-generated', 3, 480),

('ipv4-subnetting', 'cued',
 'Wie viele nutzbare Hosts hat ein /24-Netz? Wie viele ein /26?',
 '/24 = 256 - 2 = 254 nutzbare Hosts. /26 = 64 - 2 = 62 nutzbare Hosts (Netz- und Broadcast-Adresse abziehen).',
 '{"required_concepts": ["/24 = 254", "/26 = 62", "minus 2"]}',
 NULL, 2, 'ki-generated', 2, 60),

('ipv4-subnetting', 'cued',
 'CIDR-Notation für die Subnetzmaske 255.255.255.192? Wie viele Subnetze entstehen aus einem /24-Netz mit dieser Maske?',
 '255.255.255.192 = /26 (192 = 11000000, 2 zusätzliche Netzbits). Aus einem /24 entstehen 2^(26-24) = 4 Subnetze.',
 '{"required_concepts": ["/26", "192 binär", "4 Subnetze", "2^2"]}',
 NULL, 2, 'ki-generated', 3, 90),

('ipv4-subnetting', 'cued',
 'Du hast 5 Subnetze mit folgender Hostanzahl: 100, 50, 25, 12, 5. Welche CIDR-Maske wählst du jeweils und welches ist die nächste freie Subnetzadresse wenn du bei 192.168.1.0 anfängst (lückenlos)?',
 'Nach Hostanzahl absteigend sortieren (schon korrekt). 100 → /25 (126 hosts) → 192.168.1.0/25 → freie Adresse 192.168.1.128. 50 → /26 (62) → 192.168.1.128/26 → freie 192.168.1.192. 25 → /27 (30) → 192.168.1.192/27 → freie 192.168.1.224. 12 → /28 (14) → 192.168.1.224/28 → freie 192.168.1.240. 5 → /29 (6) → 192.168.1.240/29.',
 '{"required_concepts": ["/25", "/26", "/27", "/28", "/29", "lückenlos", "192.168.1.0", "192.168.1.128", "192.168.1.192", "192.168.1.224"]}',
 NULL, 6, 'ki-generated', 4, 480),

('ipv4-subnetting', 'cued',
 'Was ist die Broadcast-Adresse des Netzes 10.0.16.0/20?',
 '/20 hat 12 Hostbits. 16 dezimal = 0001 0000 binär. Erste 4 Bits des dritten Oktetts gehören zum Netz. Broadcast: alle Hostbits = 1, also 0001 1111 = 31 im dritten Oktett, 255 im vierten. → 10.0.31.255',
 '{"required_concepts": ["10.0.31.255", "/20", "Broadcast", "12 Hostbits"]}',
 NULL, 3, 'ki-generated', 4, 180),

('ipv4-subnetting', 'application',
 'Standorte mit Hostanzahl: A=129, B=59, C=30, D=141, E=81, F=159, G=25, H=43. Erstelle ein lückenloses VLSM-Adresskonzept beginnend bei 172.16.128.0. Berücksichtige auch 1 Router-Interface pro Standort. Gib pro Standort an: Subnetzadresse mit CIDR.',
 'Sortierung absteigend (Hosts + 1 Router): F(160), D(142), A(130), E(82), B(60), H(44), C(31), G(26).\n\nF: 172.16.128.0/24 (256 - 2 = 254 ≥ 160)\nD: 172.16.129.0/24\nA: 172.16.130.0/24\nE: 172.16.131.0/25 (128 - 2 = 126 ≥ 82)\nB: 172.16.131.128/26 (64 - 2 = 62 ≥ 60)\nH: 172.16.131.192/26 (62 ≥ 44)\nC: 172.16.132.0/27 (32 - 2 = 30 ≥ 31 — NEIN, brauchen /26)\n\nKorrektur: C(31) → /27 reicht nicht (nur 30 Hosts). Nimm /26.\nC: 172.16.132.0/26\nG: 172.16.132.64/27 (30 ≥ 26)',
 '{"required_concepts": ["absteigend sortieren", "lückenlos", "VLSM", "CIDR", "alle 8 Standorte", "Router einberechnet"]}',
 '[{"criterion": "Sortierung", "weight": 2, "description": "Absteigend nach Hostanzahl", "required": true},
   {"criterion": "Lückenlos", "weight": 4, "description": "Keine Lücken zwischen Subnetzen", "required": true},
   {"criterion": "Korrekte CIDR-Wahl", "weight": 6, "description": "Kleinste passende Maske, Router berücksichtigt", "required": true},
   {"criterion": "Vollständigkeit", "weight": 4, "description": "Alle 8 Standorte", "required": true}]',
 16, 'W2324-PB2-1.6', 5, 1500),

-- ============================================================
-- 3. IPv6-Subnetting
-- ============================================================

('ipv6-subnetting', 'blurt',
 'Schreibe alles auf was du über IPv6 weißt: Adresslänge, Notation, Kurzform-Regeln, EUI-64, Link-Local vs Global, Präfixlänge, Subnetting.',
 'IPv6 = 128 Bit, geschrieben als 8 Gruppen à 4 Hex-Stellen, getrennt durch ":". Kurzformregeln: 1) Führende Nullen pro Gruppe weglassen (0db8 → db8). 2) Eine zusammenhängende Folge von Null-Gruppen einmal durch "::" ersetzen (kann nur EINMAL pro Adresse). EUI-64: aus MAC-Adresse 64-Bit Interface-ID bilden — MAC in 2 Hälften teilen, "FFFE" in die Mitte einfügen, 7. Bit (Universal/Local) flippen. Link-Local: fe80::/10 (nur lokal, nicht routbar). Global Unicast: 2000::/3 (z.B. 2001:db8::/32). Standard-Subnet ist /64 — 64 Bit Präfix + 64 Bit Interface-ID.',
 '{"required_concepts": ["128 Bit", "8 Gruppen 4 Hex", "Kurzform fuehrende Nullen", "Doppelpunkt einmal", "EUI-64", "MAC FFFE", "7. Bit flippen", "fe80 Link-Local", "2000 Global", "/64 Standard"]}',
 '[{"criterion": "Adresslänge + Notation", "weight": 2, "description": "128 Bit, Hex-Gruppen", "required": true},
   {"criterion": "Kurzform-Regeln", "weight": 3, "description": "Beide Regeln + Doppelpunkt nur einmal", "required": true},
   {"criterion": "EUI-64 Verfahren", "weight": 3, "description": "FFFE einfügen, 7. Bit flippen", "required": true},
   {"criterion": "Adresstypen", "weight": 2, "description": "Link-Local vs Global mit Präfixen", "required": true}]',
 10, 'ki-generated', 3, 480),

('ipv6-subnetting', 'cued',
 'Kürze die IPv6-Adresse 2001:0db8:0000:0000:0001:0000:0000:0001 in Kurzform (2 Möglichkeiten erläutern, eine wählen).',
 'Möglichkeit 1: 2001:db8::1:0:0:1 (führende Nullen weg, ersten Null-Block durch :: ersetzen).\nMöglichkeit 2: 2001:db8:0:0:1::1 (zweiten Null-Block durch :: ersetzen).\n\nNur eine :: ist erlaubt — nicht beide gleichzeitig. Längster Null-Block bevorzugt — beide sind hier 2 Gruppen lang, also beide Varianten zulässig.',
 '{"required_concepts": ["2001:db8", "Doppelpunkt nur einmal", "längsten Block ersetzen", "fuehrende Nullen weglassen"]}',
 NULL, 3, 'ki-generated', 3, 180),

('ipv6-subnetting', 'cued',
 'MAC-Adresse: 00:1A:2B:3C:4D:5E. Bilde mit EUI-64 die Interface-ID für eine IPv6-Adresse.',
 'Schritt 1: MAC in 2 Hälften: 00:1A:2B | 3C:4D:5E. \nSchritt 2: FFFE einfügen: 00:1A:2B:FF:FE:3C:4D:5E. \nSchritt 3: 7. Bit des ersten Bytes flippen (Universal/Local-Flag): 00 = 0000 0000 → 0000 0010 = 02. \nResultat: 021A:2BFF:FE3C:4D5E.',
 '{"required_concepts": ["FFFE einfügen", "7. Bit flippen", "021A", "2BFF FE3C 4D5E"]}',
 NULL, 4, 'ki-generated', 4, 240),

('ipv6-subnetting', 'cued',
 'Wie viele /64-Subnetze können aus dem Präfix 2001:db8:42::/56 gebildet werden?',
 '2^(64-56) = 2^8 = 256 Subnetze.',
 '{"required_concepts": ["256", "2^8", "/56 zu /64"]}',
 NULL, 2, 'ki-generated', 3, 60),

('ipv6-subnetting', 'cued',
 'Was ist eine Link-Local-Adresse in IPv6? Welches Präfix hat sie und wofür wird sie genutzt?',
 'Link-Local hat Präfix fe80::/10 (in der Praxis fe80::/64). Sie ist nur im lokalen Netzwerksegment gültig — wird nicht über Router weitergeleitet. Genutzt für: Neighbor Discovery (NDP), Router Advertisement, Auto-Konfiguration. Jedes IPv6-Interface hat automatisch eine Link-Local.',
 '{"required_concepts": ["fe80", "/10 oder /64", "lokal", "nicht routbar", "NDP", "Router Advertisement"]}',
 NULL, 3, 'ki-generated', 3, 120),

('ipv6-subnetting', 'application',
 'Vom Provider erhältst du das Präfix 2001:db8:ea:2300::/56. Du sollst pro VLAN ein /64-Subnetz vergeben für: Admin (VLAN 10), Vertrieb (VLAN 20), Gäste (VLAN 30). Gib für jedes VLAN das /64-Subnetz an. Konfiguriere zusätzlich die globale IPv6-Adresse für den Admin-PC mit ID :ab01 manuell.',
 'Vom /56-Präfix sind 8 weitere Bits für Subnetting verfügbar (56 → 64 = 8 Bit = 256 mögliche /64).\nVLAN 10 Admin: 2001:db8:ea:2310::/64\nVLAN 20 Vertrieb: 2001:db8:ea:2320::/64\nVLAN 30 Gäste: 2001:db8:ea:2330::/64\n\nAdmin-PC manuell: globale Adresse = Subnetz-Präfix + Interface-ID\n→ 2001:db8:ea:2310::ab01/64\nGateway: in der Regel 2001:db8:ea:2310::1/64 (Router-Interface)\nDNS: meist Link-Local des DNS-Servers, z.B. fe80::d/64',
 '{"required_concepts": ["/56 zu /64 = 8 Bit", "256 Subnetze möglich", "VLAN-Subnetze unterschiedlich", "globale IPv6 mit Interface-ID", "Gateway Router-Interface"]}',
 '[{"criterion": "Subnetz pro VLAN", "weight": 4, "description": "Jedes VLAN eigenes /64", "required": true},
   {"criterion": "Globale Admin-PC-Adresse", "weight": 2, "description": "Subnetz + ::ab01", "required": true},
   {"criterion": "Gateway + DNS", "weight": 2, "description": "Sinnvolle Konfiguration", "required": true}]',
 8, 'AP1-2026-3.4', 4, 600)

) AS v(slug, item_type, prompt, model_answer, expected_answer_structure,
       grading_criteria, points, source_exam, difficulty, estimated_time_sec)
JOIN topic_lookup t ON t.slug = v.slug
ON CONFLICT DO NOTHING;
