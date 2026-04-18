-- ============================================================================
-- Migration: 124_ap2_seed_keythemes_part2.sql
-- Description: Seed Teil 2 — USV, OSI-Troubleshooting, Zuschlagskalkulation.
--              Fortsetzung von 123_ap2_seed_keythemes.sql.
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
-- 3. USV (Unterbrechungsfreie Stromversorgung)
-- ============================================================

('usv', 'blurt',
 'Schreibe alles was du über USV (Unterbrechungsfreie Stromversorgung) weißt: drei Klassen (VFD/VI/VFI), Berechnung der Überbrückungszeit, Leistungsfaktor, Wann welche Klasse sinnvoll ist.',
 'Drei USV-Klassen nach EN 62040-3:\n- VFD (Voltage and Frequency Dependent / Off-Line / Standby): einfachste Form, Akku springt erst bei Stromausfall ein. Schaltzeit 4-8 ms. Günstig, für unkritische PCs.\n- VI (Voltage Independent / Line-Interactive): Spannung wird kontinuierlich geregelt (AVR), aber Frequenz nicht. Schaltzeit 2-4 ms. Mittlerer Schutz, für Workstations/kleine Server.\n- VFI (Voltage and Frequency Independent / Online / Doppelwandler): Eingangsstrom wird konstant in Gleichstrom + zurück in Wechselstrom gewandelt — keine Schaltzeit, perfekte Sinuskurve. Teurer, für Server und Rechenzentren.\n\nÜberbrückungszeit: t = (Akkukapazität in Ah × Spannung × cos φ) / Last in W. Leistungsfaktor cos φ ≈ 0.8-0.9 für moderne Geräte.\n\nVA vs Watt: VA = Scheinleistung, W = Wirkleistung. W = VA × cos φ.',
 '{"required_concepts": ["VFD Off-Line", "VI Line-Interactive", "VFI Online Doppelwandler", "Schaltzeit", "Überbrückungszeit Formel", "cos phi", "VA vs Watt", "Wann welche Klasse"]}',
 '[{"criterion": "3 USV-Klassen benannt", "weight": 3, "description": "VFD/VI/VFI mit Erklärung", "required": true},
   {"criterion": "Schaltzeit-Vergleich", "weight": 2, "description": "0 vs 2-4 vs 4-8 ms", "required": true},
   {"criterion": "Berechnungs-Formel", "weight": 2, "description": "Überbrückungszeit", "required": true},
   {"criterion": "VA/W Unterscheidung", "weight": 1, "description": "Scheinleistung vs Wirkleistung", "required": false}]',
 8, 'ki-generated', 4, 480),

('usv', 'cued',
 'Was bedeuten die USV-Abkürzungen VFD, VI und VFI nach EN 62040-3?',
 'VFD = Voltage and Frequency Dependent (Off-Line/Standby).\nVI = Voltage Independent (Line-Interactive).\nVFI = Voltage and Frequency Independent (Online/Doppelwandler).',
 '{"required_concepts": ["Voltage Frequency Dependent", "Voltage Independent", "Voltage Frequency Independent"]}',
 NULL, 3, 'ki-generated', 2, 90),

('usv', 'cued',
 'Wann ist eine VFI-USV (Online/Doppelwandler) gegenüber einer VFD- oder VI-USV unbedingt notwendig?',
 'Wenn KEINE Schaltzeit toleriert werden darf (z.B. lebenswichtige medizinische Geräte, Server-RZ mit Datenbanken/Transaktionen) ODER wenn der Eingangsstrom stark schwankt (Frequenz-Probleme, Spannungs-Spitzen). VFI wandelt kontinuierlich AC → DC → AC, daher 0 ms Schaltzeit und perfekte Sinuskurve.',
 '{"required_concepts": ["keine Schaltzeit", "0 ms", "Doppelwandler", "Frequenz-Probleme", "Server", "Rechenzentrum"]}',
 NULL, 3, 'ki-generated', 3, 120),

('usv', 'cued',
 'Eine USV hat eine Akkukapazität von 12 Ah bei 24 V. Cos φ = 0.8. Wie lange überbrückt sie eine Last von 200 W?',
 'Verfügbare Energie: 12 Ah × 24 V = 288 Wh (Scheinleistung).\nWirkleistung verfügbar: 288 × 0.8 = 230.4 Wh.\nÜberbrückungszeit: 230.4 Wh / 200 W = 1.152 h ≈ 69 Minuten.',
 '{"required_concepts": ["12 × 24 = 288", "0.8 Leistungsfaktor", "230.4", "230.4 / 200", "ca 69 min"]}',
 NULL, 4, 'ki-generated', 4, 240),

('usv', 'cued',
 'Welcher Unterschied besteht zwischen VA (Scheinleistung) und W (Wirkleistung) bei der USV-Auswahl?',
 'VA = Scheinleistung (Voltampere) = Spannung × Strom — gibt die Größe an, die die USV liefern kann.\nW = Wirkleistung (Watt) = VA × cos φ — die tatsächlich nutzbare Leistung für ohmsche Lasten.\n\nUSV-Hersteller geben oft VA an. Daher umrechnen: bei cos φ = 0.7 reicht eine 1000 VA USV für 700 W Last. Bei modernen Geräten cos φ ≈ 0.9-1.0 (PFC-Netzteile).',
 '{"required_concepts": ["VA Scheinleistung", "W Wirkleistung", "cos phi Faktor", "Hersteller VA"]}',
 NULL, 3, 'ki-generated', 4, 180),

('usv', 'application',
 'Server-Rack hat folgende Verbraucher: 2× Server à 350 W, 1× Switch 80 W, 1× Storage 240 W. Du sollst eine USV auswählen die mindestens 15 Min bei Volllast überbrückt. Akku-Kapazität verfügbar: 24 V Akkus mit 7 Ah, 9 Ah, 12 Ah, 18 Ah. Cos φ = 0.85. Berechne welche Akku-Größe ausreicht und wie groß (in VA) die USV mindestens sein muss.',
 'Gesamtlast: 2×350 + 80 + 240 = 1020 W.\n\nUSV-Größe in VA: P = VA × cos φ → VA = 1020 / 0.85 = 1200 VA. Wähle nächstgrößere Standard-USV: 1500 VA.\n\nGewünschte Überbrückungszeit: 15 Min = 0.25 h.\nBenötigte Energie: 1020 W × 0.25 h = 255 Wh Wirkleistung.\nIn Wh Scheinleistung: 255 / 0.85 = 300 Wh.\nBei 24 V: 300 / 24 = 12.5 Ah Akku nötig.\n\nWähle 18 Ah Akku (12 Ah reicht knapp nicht — 12 × 24 × 0.85 = 244.8 Wh / 1020 W = 0.24 h ≈ 14.4 Min, < 15 Min).',
 '{"required_concepts": ["1020 W Gesamtlast", "VA = W / cos phi", "1500 VA gewählt", "12.5 Ah benötigt", "18 Ah gewählt", "12 Ah reicht nicht"]}',
 '[{"criterion": "Lastberechnung", "weight": 1, "description": "1020 W Summe", "required": true},
   {"criterion": "VA-Berechnung", "weight": 2, "description": "W/cos phi", "required": true},
   {"criterion": "Energiebedarf", "weight": 2, "description": "Wh über 15 Min", "required": true},
   {"criterion": "Akku-Wahl mit Begründung", "weight": 3, "description": "12 Ah zu klein, 18 Ah passt", "required": true}]',
 8, 'W2022-PB3-1.5', 5, 900),

-- ============================================================
-- 4. OSI-Troubleshooting
-- ============================================================

('osi-troubleshooting', 'blurt',
 'Beschreibe die 7 OSI-Schichten mit jeweils 1-2 Beispielprotokollen oder Geräten und 1-2 typischen Fehlerbildern + Test-Tools für jede Schicht.',
 'L1 Physical: Kabel, Stecker, Hub, Repeater. Protokolle/Standards: Ethernet (Layer-1-Teil), DSL, LWL. Fehler: Kabelbruch, lose Stecker. Test: LED-Status, Kabeltester.\nL2 Data Link: MAC-Adresse, Switch, Bridge. Protokolle: Ethernet (Layer-2), VLAN (802.1Q), STP, ARP. Fehler: falsches VLAN, MAC-Konflikt. Test: show vlan, show mac, arping.\nL3 Network: IP, Router. Protokolle: IPv4/IPv6, ICMP, OSPF, RIP. Fehler: falsche IP/Maske/Gateway, Routing-Loops. Test: ping, traceroute, show ip route.\nL4 Transport: TCP, UDP, Port. Fehler: Port blockiert, Firewall. Test: telnet IP PORT, netstat, nmap.\nL5 Session: Auf-/Abbau von Sessions. Protokolle: NetBIOS, RPC. Fehler: Session-Timeout. Test: Session-Logs.\nL6 Presentation: Verschlüsselung, Encoding. Protokolle: TLS/SSL, JPEG, ASCII. Fehler: TLS-Handshake. Test: openssl s_client.\nL7 Application: HTTP, FTP, SMTP, DNS. Fehler: Service nicht erreichbar, DNS falsch. Test: nslookup, curl, browser.',
 '{"required_concepts": ["L1 Physical", "L2 Data Link MAC VLAN", "L3 Network IP Routing", "L4 Transport TCP UDP Port", "L5 Session", "L6 Presentation TLS", "L7 Application HTTP DNS", "ping", "traceroute", "nslookup", "show vlan", "Test-Tool je Schicht"]}',
 '[{"criterion": "Alle 7 Schichten", "weight": 4, "description": "Vollständig benannt", "required": true},
   {"criterion": "Beispielprotokolle", "weight": 3, "description": "Mind. 1 pro Schicht", "required": true},
   {"criterion": "Typische Fehler", "weight": 2, "description": "Pro Schicht ein Fehlerbild", "required": false},
   {"criterion": "Test-Tools", "weight": 3, "description": "Pro Schicht ein Tool/Befehl", "required": true}]',
 11, 'ki-generated', 4, 600),

('osi-troubleshooting', 'cued',
 'Was prüft man bei Bottom-Up-Troubleshooting auf Schicht 1, und mit welchem Werkzeug?',
 'Schicht 1 Physical: physische Verbindung. Prüfen: Kabel eingesteckt? Status-LED am Switch/NIC grün? Kabel intakt? Patchfeld ok? Werkzeug: Kabeltester (PoE-Tester oder Zertifizierer wie Fluke), visueller LED-Check, Loopback-Stecker bei seriellen Verbindungen.',
 '{"required_concepts": ["Kabel", "LED Status", "Kabeltester", "physische Verbindung"]}',
 NULL, 2, 'ki-generated', 2, 90),

('osi-troubleshooting', 'cued',
 'Welche Schicht ist betroffen wenn ein Client die richtige IP hat aber andere Geräte im LAN nicht erreichen kann? Wie testest du das?',
 'Wahrscheinlich Schicht 2 (Data Link) — Switch-Port falsch im VLAN, MAC-Filter aktiv, oder STP blockiert den Port.\n\nTest: am Switch `show interface status` (Port up?), `show vlan brief` (welches VLAN?), `show mac address-table` (MAC bekannt?), `show spanning-tree` (Port blockiert?).\nAm Client: `arp -a` (MAC des Gateways aufgelöst?), `ping default-gateway` (Schicht-3-Test gibt indirekt Schicht-2-Hinweis).',
 '{"required_concepts": ["Layer 2", "Schicht 2", "VLAN", "show vlan", "show mac", "arp", "STP"]}',
 NULL, 4, 'ki-generated', 4, 240),

('osi-troubleshooting', 'cued',
 'Du kannst den Webserver per Browser nicht erreichen, ping zur IP funktioniert aber. Welche Schicht ist defekt? Welcher Test hilft?',
 'Schicht 3 (Network) ist OK (ping geht). Mögliche defekte Schicht: 4 (Port 80/443 blockiert) oder 7 (Webserver-Service down).\n\nTest Schicht 4: `telnet IP 80` oder `nc -zv IP 80` — wenn Verbindung steht, ist Schicht 4 OK.\nTest Schicht 7: wenn Schicht 4 OK aber Browser nicht: Webserver-Logs prüfen, `curl -v http://IP` für detaillierten HTTP-Fehler.',
 '{"required_concepts": ["Schicht 4 oder 7", "telnet 80", "nc oder netcat", "curl", "Webserver Logs"]}',
 NULL, 3, 'ki-generated', 4, 180),

('osi-troubleshooting', 'cued',
 'DNS-Auflösung schlägt fehl ("name resolution failed"). Auf welcher Schicht arbeitet DNS und wie testest du?',
 'DNS arbeitet auf Schicht 7 (Application), nutzt UDP/TCP Port 53 (Schicht 4).\n\nTest: `nslookup hostname` oder `dig hostname @8.8.8.8` (anderen DNS-Server testen). Mit `nslookup hostname 8.8.8.8` testet man ob der lokale DNS-Server defekt oder die Anfrage selbst falsch ist. Wenn der Test mit 8.8.8.8 klappt aber lokal nicht: lokaler DNS-Server defekt.',
 '{"required_concepts": ["Schicht 7", "Port 53", "nslookup", "dig", "alternativer DNS"]}',
 NULL, 3, 'ki-generated', 3, 180),

('osi-troubleshooting', 'application',
 'Bottom-Up-Troubleshooting: Erkläre für jede der 7 OSI-Schichten je einen typischen Fehler und die zugehörige Testmethode aus Sicht eines Sysadmins.',
 'L1 Physical — Fehler: Kabel defekt. Test: Status-LED am Switch + Kabeltester.\nL2 Data Link — Fehler: Falsches VLAN am Port. Test: `show vlan brief` + `show interface status`.\nL3 Network — Fehler: Falsche IP/Maske/Gateway. Test: `ping`, `traceroute`, `show ip route`.\nL4 Transport — Fehler: Port blockiert (Firewall). Test: `telnet IP PORT` oder `nmap`.\nL5 Session — Fehler: Session-Timeout zwischen Client und Server. Test: Application-Logs, Session-Tracking.\nL6 Presentation — Fehler: TLS-Zertifikat abgelaufen oder ungültig. Test: `openssl s_client -connect host:443`.\nL7 Application — Fehler: DNS-Auflösung scheitert. Test: `nslookup`, alternative DNS-Server probieren.',
 '{"required_concepts": ["L1-L7 alle abgedeckt", "Fehler je Schicht", "Test-Tool je Schicht", "Bottom-Up Reihenfolge", "ping", "telnet", "nslookup"]}',
 '[{"criterion": "Alle 7 Schichten", "weight": 4, "description": "Vollständig durchgegangen", "required": true},
   {"criterion": "Realistischer Fehler je Schicht", "weight": 3, "description": "Plausible Fehlerbilder", "required": true},
   {"criterion": "Test-Tools korrekt", "weight": 3, "description": "Tools passen zur Schicht", "required": true}]',
 10, 'S2024-PB3-2.4', 4, 900),

-- ============================================================
-- 5. Zuschlagskalkulation
-- ============================================================

('zuschlagskalkulation', 'blurt',
 'Schreibe das komplette Schema der Zuschlagskalkulation auf — von Materialeinzelkosten (MEK) bis zum Brutto-Verkaufspreis (Brutto-VKP). Erkläre jede Stufe.',
 'Zuschlagskalkulation Schritt-für-Schritt:\n\n1. Materialeinzelkosten (MEK)\n+ Materialgemeinkosten (MGK, in % auf MEK)\n= Materialkosten (MK)\n\n2. Fertigungseinzelkosten (FEK)\n+ Fertigungsgemeinkosten (FGK, in % auf FEK)\n= Fertigungskosten (FK)\n\n3. Materialkosten + Fertigungskosten\n= Herstellkosten (HK)\n\n4. Herstellkosten\n+ Verwaltungsgemeinkosten (VwGK, in % auf HK)\n+ Vertriebsgemeinkosten (VtGK, in % auf HK)\n= Selbstkosten (SK)\n\n5. Selbstkosten\n+ Gewinn (in % auf SK)\n= Netto-Verkaufspreis / Listenpreis\n\n6. Netto-VKP\n+ Mehrwertsteuer (i.d.R. 19%, manchmal 7% für Bücher etc.)\n= Brutto-Verkaufspreis (Brutto-VKP)\n\nManchmal noch zusätzlich: − Skonto (Zahlungsanreiz), − Rabatt, danach Netto.',
 '{"required_concepts": ["MEK", "MGK", "Materialkosten", "FEK", "FGK", "Fertigungskosten", "Herstellkosten", "VwGK", "VtGK", "Selbstkosten", "Gewinn", "Netto-VKP", "MwSt", "Brutto-VKP"]}',
 '[{"criterion": "Vollständigkeit Stufen", "weight": 4, "description": "Alle 14+ Begriffe", "required": true},
   {"criterion": "Korrekte Reihenfolge", "weight": 3, "description": "MEK → MGK → ... → Brutto", "required": true},
   {"criterion": "Zuschlagsbasis", "weight": 2, "description": "MGK auf MEK, VwGK/VtGK auf HK", "required": true},
   {"criterion": "MwSt-Stufe", "weight": 1, "description": "19/7%, am Ende", "required": false}]',
 12, 'ki-generated', 4, 600),

('zuschlagskalkulation', 'cued',
 'Was ist der Unterschied zwischen Skonto und Rabatt?',
 'Rabatt = Preisnachlass auf den Listenpreis ohne Bedingung an Zahlungszeitpunkt (z.B. Mengen-, Treue-, Wiederverkäufer-Rabatt). Wird vor der Mehrwertsteuer abgezogen.\n\nSkonto = Preisnachlass für SCHNELLE Zahlung (z.B. "2% Skonto bei Zahlung innerhalb 14 Tagen, sonst Netto 30 Tage"). Ist eine Belohnung für vorzeitige Zahlung — wird auf den Brutto-Rechnungsbetrag angewendet.',
 '{"required_concepts": ["Rabatt unbedingt", "Skonto schnelle Zahlung", "Rabatt vor MwSt", "Skonto auf Brutto", "Beispiel 2% 14 Tage"]}',
 NULL, 4, 'ki-generated', 3, 180),

('zuschlagskalkulation', 'cued',
 'Gegeben: MEK = 200 €, MGK = 25 %, FEK = 400 €, FGK = 150 %. Berechne Materialkosten, Fertigungskosten und Herstellkosten.',
 'Materialkosten: MEK + MGK% × MEK = 200 + 0.25 × 200 = 200 + 50 = 250 €\nFertigungskosten: FEK + FGK% × FEK = 400 + 1.50 × 400 = 400 + 600 = 1000 €\nHerstellkosten: 250 + 1000 = 1250 €',
 '{"required_concepts": ["MK 250", "FK 1000", "HK 1250", "MGK auf MEK", "FGK auf FEK"]}',
 NULL, 4, 'ki-generated', 3, 240),

('zuschlagskalkulation', 'cued',
 'Was umfasst die Verwaltungs- und Vertriebsgemeinkosten (VwGK + VtGK) und auf welche Basis werden sie aufgeschlagen?',
 'VwGK = Personalkosten Buchhaltung, Geschäftsführung, IT-Verwaltung, Bürokosten etc.\nVtGK = Personal Vertrieb/Marketing, Werbung, Versandkosten, Provisionen.\n\nBeide werden in % auf die HERSTELLKOSTEN (HK) aufgeschlagen, nicht auf MEK oder FEK.',
 '{"required_concepts": ["Verwaltung Personal", "Vertrieb Marketing", "auf HK", "Herstellkosten Basis"]}',
 NULL, 3, 'ki-generated', 3, 150),

('zuschlagskalkulation', 'cued',
 'Selbstkosten = 800 €, Gewinnzuschlag 20 %, MwSt 19 %. Berechne Netto-VKP und Brutto-VKP.',
 'Netto-VKP = Selbstkosten + Gewinn = 800 + 0.20 × 800 = 800 + 160 = 960 €\nMwSt-Betrag = 960 × 0.19 = 182.40 €\nBrutto-VKP = 960 + 182.40 = 1142.40 €',
 '{"required_concepts": ["Netto 960", "MwSt 182.40", "Brutto 1142.40", "20% auf SK"]}',
 NULL, 3, 'ki-generated', 3, 180),

('zuschlagskalkulation', 'application',
 'Wohlfühl-Winterbox: MEK = 1.20 €, MGK = 30 %, FEK = 3.65 €, FGK = 180 %, VwGK = 35 %, VtGK = 40 %, Gewinn = 40 %, MwSt = 7 %. Erstelle die komplette Zuschlagskalkulation in Tabellenform mit Zwischenergebnissen und gib Brutto-VKP an.',
 'Materialeinzelkosten MEK:                  1.20 €\n+ Materialgemeinkosten MGK 30%:           +0.36 €\n= Materialkosten MK:                       1.56 €\n\nFertigungseinzelkosten FEK:                3.65 €\n+ Fertigungsgemeinkosten FGK 180%:        +6.57 €\n= Fertigungskosten FK:                    10.22 €\n\nHerstellkosten HK (MK + FK):              11.78 €\n+ Verwaltungsgemeinkosten VwGK 35% auf HK: +4.123 €\n+ Vertriebsgemeinkosten VtGK 40% auf HK:  +4.712 €\n= Selbstkosten SK:                        20.615 €\n\n+ Gewinn 40% auf SK:                      +8.246 €\n= Netto-VKP / Listenpreis:                28.861 €\n+ MwSt 7%:                                 +2.020 €\n= Brutto-VKP:                             30.881 €\n\n→ Brutto-Verkaufspreis ca. 30.88 €',
 '{"required_concepts": ["MK 1.56", "FK 10.22", "HK 11.78", "SK 20.61", "Netto-VKP 28.86", "Brutto 30.88", "alle Stufen", "Tabellenform"]}',
 '[{"criterion": "Materialkosten korrekt", "weight": 1, "description": "1.56 €", "required": true},
   {"criterion": "Fertigungskosten korrekt", "weight": 2, "description": "10.22 €", "required": true},
   {"criterion": "Herstellkosten korrekt", "weight": 1, "description": "11.78 €", "required": true},
   {"criterion": "Selbstkosten korrekt", "weight": 3, "description": "VwGK + VtGK auf HK", "required": true},
   {"criterion": "Netto/Brutto korrekt", "weight": 3, "description": "Gewinn + MwSt", "required": true},
   {"criterion": "Tabellenform", "weight": 2, "description": "Übersichtliche Darstellung", "required": false}]',
 12, 'W2023-PB3-1.1', 4, 900),

('zuschlagskalkulation', 'application',
 'RÜCKWÄRTSKALKULATION (AP1 2026 Aufg. 2.1): Gegeben Barverkaufspreis 1000 €, Handlungskosten 20 %, Lieferer-Rabatt 10 %, Gewinn 5 %, Bezugskosten 25 €, Lieferer-Skonto 3 %. Ermittle den Listeneinkaufspreis.',
 'Vorgehen: Vom Barverkaufspreis rückwärts zum Listeneinkaufspreis.\n\nBarverkaufspreis (gegeben):                 1000.00 €\n− Gewinn 5 %:           Selbstkosten = BVP / 1.05 = 952.38 €\n− Handlungskosten 20 %: Bezugspreis = 952.38 / 1.20 = 793.65 €\n− Bezugskosten:         Bareinkaufspreis = 793.65 − 25 = 768.65 €\n+ Skonto 3 %:           Zieleinkaufspreis = 768.65 / 0.97 = 792.42 €\n+ Rabatt 10 %:          Listeneinkaufspreis = 792.42 / 0.90 = 880.46 €\n\n→ Listeneinkaufspreis ≈ 880.47 €\n\n(Beachte: Skonto und Rabatt werden DIVIDIERT durch (1 - Prozentsatz), nicht abgezogen — denn wir wollen den ursprünglichen Wert bevor Abzüge.)',
 '{"required_concepts": ["Selbstkosten 952.38", "Bezugspreis 793.65", "Bareinkaufspreis 768.65", "Zieleinkaufspreis 792.42", "Listenpreis 880.47", "rueckwärts dividieren", "Bezugskosten subtrahieren"]}',
 '[{"criterion": "Selbstkosten", "weight": 2, "description": "BVP / 1.05", "required": true},
   {"criterion": "Bezugspreis", "weight": 2, "description": "/ 1.20", "required": true},
   {"criterion": "Bezugskosten abziehen", "weight": 1, "description": "− 25 €", "required": true},
   {"criterion": "Skonto + Rabatt rückwärts", "weight": 3, "description": "/ 0.97 dann / 0.90", "required": true},
   {"criterion": "Listenpreis korrekt", "weight": 2, "description": "ca. 880.47 €", "required": true}]',
 10, 'AP1-2026-2.1', 5, 900)

) AS v(slug, item_type, prompt, model_answer, expected_answer_structure,
       grading_criteria, points, source_exam, difficulty, estimated_time_sec)
JOIN topic_lookup t ON t.slug = v.slug
ON CONFLICT DO NOTHING;
