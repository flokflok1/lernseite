-- ============================================================================
-- Migration: 140_ap2_module_netzplan.sql
-- Description: Modul "Netzplan lesen + Geräte erkennen". Lehrblock + ~25
--              Aufgaben im Pool.
--              Schwerpunkte: Geräte-Identifikation (OSI-Schicht), Subnetze
--              ableiten, Konfiguration aus Plan, Fehlersuche-Pfade,
--              VLAN/DMZ-Erkennung.
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-04-19
-- ============================================================================

INSERT INTO assessments.ap2_modules
    (slug, name_de, description, theory_markdown,
     estimated_min, difficulty, sort_order, prerequisite_slugs, is_active)
VALUES (
    'netzplan-lesen',
    'Netzplan lesen + Geräte + Subnetze',
    'Netzwerktopologie analysieren: Geräte erkennen, OSI-Schicht zuordnen, Subnetze ableiten, Fehlersuche-Pfade. Standard in jeder AP2-Netzwerk-Aufgabe.',
$theory$
## Geräte im Netzplan — wer macht was?

| Gerät | OSI-Schicht | Aufgabe | Erkennen im Plan |
|---|---|---|---|
| **Repeater / Hub** | L1 (Bitübertragung) | verstärkt Signal, kein Verständnis von Adressen | mehrere Ports, alle "blind" verbunden |
| **Switch** | L2 (Sicherung) | leitet Frames anhand MAC weiter | mehrere Ports, oft als Rechteck mit "≣" |
| **Router** | L3 (Vermittlung) | routet Pakete zwischen Subnetzen anhand IP | meist als Kreis/Rechteck mit Pfeilen, Grenze zwischen Netzen |
| **Layer-3-Switch** | L2+L3 | Switch der auch routen kann | Switch-Symbol + Routing-Funktion |
| **Firewall** | L3-L7 | filtert Pakete nach Regeln | meist als Mauer-/Schloss-Symbol, an Netz-Grenzen |
| **Access Point** | L1+L2 | WLAN-Anbindung (Funk + MAC) | Antennen-Symbol, oft am Switch |
| **Server** | — | bietet Dienste (DNS, DHCP, Web, Mail) | Symbol + Beschriftung "Server" / Hostname |
| **Modem / Gateway** | L1+L2 (modem) bzw. L3 | Verbindung zum Provider/Internet | meist am oberen Rand des Plans, "Internet" daneben |

---

## Subnetze aus dem Plan ableiten

**Faustregel:** Jedes Subnetz wird durch einen ROUTER getrennt.
Geräte hinter demselben Switch ohne dazwischenliegenden Router = gleiches Subnetz.

Beispielausschnitt:
```
   Internet
      |
   [Router R1] ── 192.168.1.0/24 (DMZ) ── [Webserver]
      |
   192.168.10.0/24 (LAN)
   /         |          \
[Switch1] [Switch2]  [WLAN-AP]
   |          |         (≡)
[PC1, PC2] [Server]  [Smartphones]
```

Ablesbar:
- 2 Subnetze: 192.168.1.0/24 (DMZ) und 192.168.10.0/24 (LAN)
- DMZ enthält Webserver — vom Internet erreichbar, vom LAN getrennt
- Im LAN: PCs + Server + WLAN — alle gleiches Subnetz weil hinter demselben Router
- WLAN könnte über Routing/VLAN trotzdem getrennt sein (zeigt der Plan oft separat als VLAN-ID)

---

## DMZ erkennen

DMZ = Demilitarized Zone = Subnetz zwischen externem (Internet) und internem (LAN) Netz, getrennt durch (mind.) eine Firewall. Enthält nach außen erreichbare Server (Web, Mail, DNS).

**Erkennungsmerkmal im Diagramm:**
- Eigenes Subnetz neben dem internen LAN
- Direkt erreichbar vom Internet (durch Firewall)
- Server in DMZ haben KEINE direkte Verbindung ins interne LAN (Schutz)

Zwei Bauformen:
1. **Einstufig** (one-armed DMZ): eine Firewall mit drei Interfaces (Internet / DMZ / LAN). Günstiger, schwächere Trennung.
2. **Zweistufig** (back-to-back DMZ): zwei Firewalls in Reihe, DMZ zwischen ihnen. Sicherer, teurer — Standard für Unternehmen mit erhöhten Anforderungen.

---

## VLAN im Netzplan

VLANs trennen logisch was physisch am gleichen Switch hängt. Erkennbar durch:
- VLAN-IDs im Diagramm (z.B. "VLAN 10 = Mitarbeiter, VLAN 20 = Gäste")
- Trunk-Verbindungen zwischen Switches mit "T:10,20,30" oder ähnlichem
- Ports am Switch markiert mit Farbe oder VLAN-Tag

---

## Standardvorgehen Fehlersuche von Layer 1 nach oben

| Layer | Symptom | Tool |
|---|---|---|
| L1 | LED rot/aus, kein Link | LED prüfen, Kabel tauschen, ethtool |
| L2 | falsches VLAN, MAC-Konflikt | switch show vlan, arp -a |
| L3 | falsches Gateway/Subnetz | ipconfig, ping Gateway, traceroute |
| L4 | Port blockiert (Firewall) | telnet IP PORT, netstat -tln |
| L7 | Anwendung antwortet nicht, DNS falsch | nslookup, curl, Browser-Devtools |

Bei einer Aufgabe „User X kann nicht auf Server Y zugreifen, finde den Fehler" → **immer von unten nach oben** prüfen.
$theory$,
    14, 4, 3,
    '[]'::jsonb, TRUE
)
ON CONFLICT (slug) DO UPDATE SET
    name_de = EXCLUDED.name_de,
    description = EXCLUDED.description,
    theory_markdown = EXCLUDED.theory_markdown,
    sort_order = EXCLUDED.sort_order;

-- ============================================================
-- Aufgaben-Pool
-- ============================================================

WITH topic_lookup AS (
    SELECT topic_id FROM assessments.ap2_topics WHERE slug = 'netzwerkanalyse' LIMIT 1
)
INSERT INTO assessments.ap2_learning_items
    (topic_id, item_type, prompt, model_answer, expected_answer_structure,
     grading_criteria, points, source_exam, difficulty, estimated_time_sec)
SELECT (SELECT topic_id FROM topic_lookup), v.item_type, v.prompt, v.model_answer,
       v.expected_answer_structure::jsonb,
       v.grading_criteria::jsonb,
       v.points, v.source_exam, v.difficulty, v.estimated_time_sec
FROM (VALUES

-- ============================================================
-- Mastery Pool — Geräte-Identifikation (Tier 1-2)
-- ============================================================

('cued',
 'Welche OSI-Schicht arbeitet ein Switch und ein Router? Was ist der praktische Unterschied?',
 'Switch: Layer 2 (Sicherung). Leitet Ethernet-Frames anhand MAC-Adressen weiter. Bleibt INNERHALB eines Subnetzes.\n\nRouter: Layer 3 (Vermittlung). Leitet IP-Pakete zwischen verschiedenen Subnetzen weiter, anhand IP-Adressen + Routing-Tabelle. Verbindet Netze.\n\nPraktischer Unterschied: ein Switch kennt nur seine MAC-Tabelle und das angeschlossene Subnetz. Ein Router muss wissen, "wo welches Subnetz ist" und entscheidet anhand der Ziel-IP, über welches Interface das Paket muss. Layer-3-Switches kombinieren beides — sie können sowohl L2-switching als auch L3-routing.',
 '{"required_concepts": ["Switch L2 MAC", "Router L3 IP", "ein Subnetz vs Subnetze verbinden", "Routing-Tabelle"]}',
 NULL, 4, 'module-netzplan', 2, 180),

('cued',
 'Was ist eine DMZ und wie erkennst du sie im Netzplan?',
 'DMZ (Demilitarized Zone) = Pufferzone zwischen Internet und internem Netz, getrennt durch (mindestens) eine Firewall. Enthält von außen erreichbare Server wie Webserver, Mailserver, DNS.\n\nErkennungsmerkmale im Plan:\n- Eigenes Subnetz, separate IP-Range\n- Liegt zwischen Internet (oben) und LAN (unten)\n- Server in DMZ sind direkt vom Internet erreichbar (durch Firewall-Regeln)\n- KEINE direkten Verbindungen von DMZ ins interne LAN — wenn DMZ-Server kompromittiert wird, kommt Angreifer NICHT ins interne Netz\n\nZwei Bauformen:\n1. Einstufig: eine Firewall mit 3 Interfaces (Internet/DMZ/LAN)\n2. Zweistufig: zwei Firewalls hintereinander, DMZ dazwischen → sicherer',
 '{"required_concepts": ["Pufferzone", "Internet zu LAN", "Firewall-getrennt", "Web/Mail/DNS außen erreichbar", "einstufig zweistufig"]}',
 NULL, 4, 'module-netzplan', 3, 180),

('cued',
 'Wie viele Subnetze sind in einem Netzplan vorhanden? Wie zählst du sie ab?',
 'Faustregel: jedes Mal wenn ein **Router** dazwischen liegt, beginnt ein neues Subnetz.\n\nVorgehen:\n1. Router im Plan identifizieren\n2. Jeden Router-Port (Interface) anschauen\n3. Was an einem Interface hängt = ein Subnetz\n4. Geräte hinter demselben Switch (ohne Router dazwischen) = ein Subnetz\n\nAchtung: VLANs können mehrere logische Subnetze AUF demselben physischen Switch erzeugen — die zählt man auch separat. Im Plan oft als VLAN-ID markiert.\n\nEine typische Mittelstands-Topologie hat: 1× DMZ, 1× internes LAN, 1× Management-Netz, 1-2× WLAN-Subnetze = 4-5 Subnetze.',
 '{"required_concepts": ["Router trennt Subnetze", "Router-Interface = Subnetz", "Switch = ein Subnetz", "VLAN extra"]}',
 NULL, 4, 'module-netzplan', 3, 180),

('cued',
 'Was ist der Unterschied zwischen einer einstufigen und einer zweistufigen DMZ? Wann nutzt man welche?',
 'Einstufige DMZ ("Three-Legged Firewall"):\n- EINE Firewall mit drei Interfaces: Internet, DMZ, internes LAN\n- Günstiger, einfacher zu warten\n- Schwäche: wenn die eine Firewall kompromittiert ist, sind ALLE Zonen gefährdet\n- Geeignet für: kleine Unternehmen, geringer Schutzbedarf\n\nZweistufige DMZ ("Back-to-Back Firewall"):\n- ZWEI Firewalls hintereinander, DMZ dazwischen\n- Idealerweise von verschiedenen Herstellern (Defense in Depth)\n- Angreifer muss BEIDE Firewalls überwinden, um ins interne Netz zu kommen\n- Geeignet für: Unternehmen mit erhöhten Schutzanforderungen, BSI-Grundschutz, Banken, Versicherungen\n- Teurer (zwei Firewalls + Wartung), aber deutlich sicherer\n\nFalle: Manche zweistufigen Setups verwenden zwei Firewalls vom selben Hersteller — bei einer 0-Day-Lücke betrifft sie beide. Echte "Defense in Depth" = verschiedene Hersteller.',
 '{"required_concepts": ["einstufig 3 Interfaces", "zweistufig 2 Firewalls", "verschiedene Hersteller", "Defense in Depth"]}',
 NULL, 4, 'module-netzplan', 3, 240),

-- ============================================================
-- Application — Aus konkretem Netzplan Konfiguration ableiten
-- ============================================================

('application',
 'Folgender Netzplan ist gegeben:

```
                  Internet
                     |
              [Modem / Provider]
                     |
              [Firewall extern]
                     |
        ┌────────────┴────────────┐
        |                          |
   192.168.10.0/24            DMZ 192.168.20.0/24
   (internes LAN)             |
        |                  [Webserver]
   [Switch1]               [Mailserver]
   /        \                  |
 [Switch2] [WLAN-AP]      [Firewall intern]
   |          |
 [PCs]    [Smartphones]
```

(a) Wie viele Subnetze sind im Plan vorhanden?
(b) Welche Bauform der DMZ wird verwendet (einstufig/zweistufig)? Begründe.
(c) Auf welcher OSI-Schicht arbeiten die Geräte: Switch1, Firewall extern, Modem, WLAN-AP?',
 '(a) **3 Subnetze** sind vorhanden:\n  - Internet (öffentlich, vor dem Modem)\n  - 192.168.10.0/24 internes LAN (unter Firewall extern, hinter Switch1)\n  - 192.168.20.0/24 DMZ (zwischen Firewall extern und Firewall intern)\n\n(b) **Zweistufige DMZ**. Begründung: Es gibt ZWEI Firewalls hintereinander. Die externe Firewall trennt Internet von DMZ + LAN. Die interne Firewall trennt DMZ vom LAN-Verkehr (vermutlich nur erlaubte Antworten). DMZ liegt zwischen den beiden Firewalls — klassische Back-to-Back-Bauform.\n\n(c) OSI-Schichten:\n  - Switch1: **Layer 2** (Sicherung) — leitet Frames anhand MAC weiter\n  - Firewall extern: **Layer 3-7** — paketfilternd auf L3/L4 + ggf. Application Layer Inspection\n  - Modem: **Layer 1-2** — wandelt Provider-Signal (DSL/Kabel) in Ethernet, MAC-Ebene\n  - WLAN-AP: **Layer 1-2** — Funk (L1) + MAC-Frames (L2). Manche APs können auch L3 wenn sie routen.',
 '{"required_concepts": ["3 Subnetze", "Internet, LAN, DMZ", "zweistufig", "zwei Firewalls", "Switch L2", "Firewall L3-L7", "Modem L1-L2", "AP L1-L2"]}',
 '[{"criterion": "3 Subnetze identifiziert", "weight": 3, "description": "Internet/LAN/DMZ", "required": true},
   {"criterion": "Zweistufig erkannt + begründet", "weight": 4, "description": "mit Hinweis auf 2 Firewalls", "required": true},
   {"criterion": "OSI-Layer richtig", "weight": 5, "description": "alle 4 Geräte", "required": true}]',
 12, 'module-netzplan', 4, 720),

('application',
 'Im Netzplan eines Beratungsunternehmens siehst du:

```
Internet ── [Router] ── [Firewall] ── 10.0.10.0/24 ── [PCs Buchhaltung]
                          |
                       Trunk
                          |
                  [Core-Switch (L3)]
                  /       |       \
              VLAN 20  VLAN 30  VLAN 99
            10.0.20    10.0.30   10.0.99
              .0/24     .0/24    .0/24
            (Vertrieb) (Gäste)  (Mgmt)
```

(a) Wie viele Subnetze sind im internen Netz?
(b) Welche Funktion hat der "Core-Switch (L3)"?
(c) Was bedeutet "Trunk" zwischen Firewall und Core-Switch?
(d) Welches der vier Subnetze ist vermutlich am stärksten abgeschirmt vom Rest? Begründe.',
 '(a) **4 interne Subnetze**: Buchhaltung 10.0.10.0/24, Vertrieb (VLAN 20) 10.0.20.0/24, Gäste (VLAN 30) 10.0.30.0/24, Management (VLAN 99) 10.0.99.0/24.\n\n(b) Der **Core-Switch L3** ist ein Layer-3-Switch — er kombiniert Switching (L2) mit Routing (L3). Er ist für das **Inter-VLAN-Routing** zuständig: Pakete von VLAN 20 zu VLAN 30 müssen routet werden, das übernimmt der L3-Switch ohne dass ein separater Router benötigt wird. Effizienter als ein dedizierter Router weil hardwareseitig im Switch beschleunigt.\n\n(c) **Trunk-Verbindung**: ein Link der MEHRERE VLANs gleichzeitig transportiert. Pakete werden mit VLAN-Tags (IEEE 802.1Q) markiert, damit der Empfänger weiß zu welchem VLAN sie gehören. Zwischen Firewall und Core-Switch läuft also der gesamte Verkehr aller VLANs gebündelt — die Firewall kann pro VLAN unterschiedliche Regeln anwenden.\n\n(d) **VLAN 30 (Gäste) ist am stärksten abgeschirmt** — typisches Pattern: Gäste-WLAN darf nur ins Internet, NICHT in andere VLANs (Gefahr Datenabfluss / Angriffe). Die Firewall blockiert vermutlich allen Verkehr von 10.0.30.0/24 zu den anderen internen Subnetzen.\n\nAlternative: VLAN 99 (Management) wäre auch stark abgeschirmt — typisch nur für Admins zugänglich. Beide sind valide.',
 '{"required_concepts": ["4 Subnetze", "Buchhaltung Vertrieb Gäste Mgmt", "L3-Switch Inter-VLAN-Routing", "Trunk mehrere VLANs 802.1Q", "Gäste isoliert", "Mgmt isoliert"]}',
 '[{"criterion": "4 Subnetze", "weight": 2, "description": "alle benannt", "required": true},
   {"criterion": "L3-Switch Funktion", "weight": 3, "description": "Inter-VLAN-Routing", "required": true},
   {"criterion": "Trunk erklärt", "weight": 3, "description": "mehrere VLANs + 802.1Q", "required": true},
   {"criterion": "Gäste/Mgmt abgeschirmt + Begründung", "weight": 3, "description": "konkret begründet", "required": true}]',
 11, 'module-netzplan', 4, 720),

('application',
 'Ein Mitarbeiter meldet: "Ich kann auf meinem Arbeits-PC die interne Datenbank nicht erreichen. Andere PCs in der gleichen Abteilung gehen aber."\n\nBeschreibe systematisch wie du den Fehler von OSI-Layer 1 nach oben suchst. Nenne pro Layer ein konkretes Tool oder Prüfverfahren.',
 'Systematische Fehlersuche von unten nach oben:\n\n**Layer 1 (Physikalisch)**\nPrüfung: LED am Netzwerkport leuchtet? Kabel fest gesteckt? Ggf. Kabel tauschen.\nTool: `ethtool eth0` (Linux) oder Status-Anzeige im OS, LED am Switch-Port.\n\n**Layer 2 (Sicherung)**\nPrüfung: Bekommt der PC eine MAC-Auflösung des Gateways? Ist er im richtigen VLAN?\nTool: `arp -a` zeigt ob der Gateway-Eintrag da ist. `ipconfig /all` (Windows) oder `ip addr` (Linux) zeigt MAC + VLAN-Info.\n\n**Layer 3 (Vermittlung)**\nPrüfung: Hat der PC eine korrekte IP, Subnetzmaske, Gateway? Erreicht er das Gateway? Erreicht er die DB-Server-IP per Ping?\nTool: `ping <Gateway>`, `ping <DB-Server-IP>`, `tracert <DB-Server-IP>` (zeigt wo es hängt).\n\n**Layer 4 (Transport)**\nPrüfung: Antwortet der DB-Server auf dem benötigten Port (z.B. 1433 für MSSQL, 5432 für PostgreSQL, 3306 für MySQL)? Blockiert eine Firewall?\nTool: `telnet <DB-Server-IP> 5432` oder `Test-NetConnection -Port 5432` (PowerShell).\n\n**Layer 5-6 (Session/Darstellung)**\nPrüfung: TLS-Handshake erfolgreich? Korrekte Authentifizierung möglich?\nTool: bei DB selten — eher die Anwendung selbst probiert sich zu verbinden und zeigt einen TLS-/Auth-Fehler in Logs.\n\n**Layer 7 (Anwendung)**\nPrüfung: Antwortet die DB-Software überhaupt auf der Verbindung? User-Berechtigungen ok?\nTool: DB-Client (z.B. DBeaver) testet die Verbindung mit Credentials. Server-Logs der DB prüfen.\n\nWichtig: weil andere PCs in derselben Abteilung gehen, kann L1/L2/L3 zwischen Switch und DB-Server NICHT die Ursache sein — es muss am betroffenen PC selbst oder an seiner spezifischen Konfiguration liegen (z.B. lokale Firewall blockiert den Port, falsche IP-Konfig durch DHCP-Leak, Anwendungs-Cache).',
 '{"required_concepts": ["L1 LED Kabel", "L2 ARP VLAN", "L3 ping Gateway traceroute", "L4 telnet Port", "L5-6 TLS", "L7 DB-Client Logs", "andere PCs gehen → PC-spezifisch"]}',
 '[{"criterion": "Alle 7 Layer abgedeckt", "weight": 4, "description": "jede Schicht ein Tool", "required": true},
   {"criterion": "Tools korrekt", "weight": 4, "description": "passend zur Schicht", "required": true},
   {"criterion": "PC-spezifische Eingrenzung", "weight": 2, "description": "weil andere PCs gehen", "required": false}]',
 10, 'module-netzplan', 4, 720),

('application',
 'Im Netzplan siehst du:\n\n```\n[Router] ── 192.168.5.0/24 ── [Switch] ── PC1, PC2, PC3 ── [WLAN-AP] ── Smartphones\n```\n\nDie Geschäftsführung möchte, dass das WLAN ein **eigenes Subnetz** mit 192.168.6.0/24 bekommt — Gäste sollen NICHT auf interne Ressourcen zugreifen können.\n\n(a) Welche Änderung muss am Netzplan/Konfig vorgenommen werden, damit das funktioniert?\n(b) Welche zwei Begründungen sprechen FÜR diese Trennung?\n(c) Welcher aktuelle WLAN-Standard wird empfohlen und warum?',
 '(a) Notwendige Änderungen:\n\n**Option 1 (einfach):** Den WLAN-AP an einem separaten Router-Interface anschließen. Der Router hat dann zwei Interfaces: 192.168.5.0/24 (LAN) und 192.168.6.0/24 (WLAN). Routing-Regeln am Router: Verkehr von .6.0/24 nur ins Internet erlauben, nicht ins .5.0/24-LAN.\n\n**Option 2 (modern, mit VLAN):** WLAN-AP unterstützt mehrere SSIDs mit verschiedenen VLAN-IDs. Switch und AP konfigurieren mit VLAN 10 = LAN (192.168.5.0/24), VLAN 20 = Gäste-WLAN (192.168.6.0/24). Der Router routet zwischen den VLANs und blockiert Gast-zu-LAN-Verkehr per Firewall-Regel.\n\nOption 2 ist heute Standard, weil sie ohne zusätzliche Hardware auskommt und flexibler ist.\n\n(b) Zwei Begründungen für die Trennung:\n1. **Sicherheit**: Gäste-Geräte sind unkontrolliert (keine Antiviren-Pflicht, evtl. infiziert). In separatem Subnetz können sie nicht direkt auf Datei-Server, Drucker, Datenbanken zugreifen. Schutz vor Datenabfluss + Lateral Movement bei einer Infektion.\n2. **Compliance / Datenschutz**: Verarbeitung personenbezogener Daten (DSGVO) verlangt Trennung von Produktiv- und Gast-Verkehr. Bei einem Sicherheitsvorfall im Gäste-WLAN ist das interne Netz nicht betroffen.\n3. (Bonus) **Netzqualität**: Bandbreitenkontrolle pro Subnetz möglich — Gäste-WLAN kann begrenzt werden, damit es das interne Netz nicht ausbremst.\n\n(c) **IEEE 802.11ax (Wi-Fi 6)** oder neuer **802.11be (Wi-Fi 7)**.\nGründe für Wi-Fi 6:\n- Höhere Effizienz bei vielen gleichzeitigen Geräten (OFDMA)\n- Bessere Performance in dichten Umgebungen (Büro mit vielen Smartphones)\n- WPA3-Unterstützung (sicherere Verschlüsselung als WPA2)\n- Längere Akkulaufzeit für Endgeräte (Target Wake Time)\n- Abwärtskompatibel zu älteren Standards\n\nAchtung: Wi-Fi 7 kommt erst gerade auf den Markt — meist ist Wi-Fi 6 der praktische Empfehlungsstandard, Wi-Fi 7 für zukunftssichere Neubauten.',
 '{"required_concepts": ["VLAN trennen", "Router/Firewall-Regeln Gast nicht ins LAN", "Sicherheit unkontrollierte Geräte", "DSGVO Compliance", "802.11ax Wi-Fi 6", "WPA3", "OFDMA"]}',
 '[{"criterion": "Lösung mit VLAN oder separatem Subnetz", "weight": 4, "description": "konkret", "required": true},
   {"criterion": "2 Begründungen für Trennung", "weight": 3, "description": "Sicherheit + DSGVO/Compliance", "required": true},
   {"criterion": "Wi-Fi 6/802.11ax + Begründung", "weight": 3, "description": "mit OFDMA oder WPA3", "required": true}]',
 10, 'module-netzplan', 4, 600),

('cued',
 'Was bedeutet PoE (Power over Ethernet) und welche Standards gibt es?',
 'PoE = Power over Ethernet: Ein Gerät bekommt Strom und Daten über DASSELBE Netzwerkkabel. Spart eine Steckdose vor Ort und Verkabelung. Typisch für: WLAN-Access-Points, IP-Telefone, Überwachungskameras, kleine Switches.\n\nDrei Standards:\n- **IEEE 802.3af (PoE)**: bis 15,4 W am Endgerät — reicht für IP-Telefone, einfache APs.\n- **IEEE 802.3at (PoE+)**: bis 30 W — moderne WLAN-APs (Wi-Fi 5/6), Kameras mit Heizung.\n- **IEEE 802.3bt (PoE++ / Type 3+4)**: bis 60 W (Type 3) bzw. 90 W (Type 4) — High-End-APs (Wi-Fi 6E/7), Beleuchtung, Laptops.\n\nVoraussetzung: Switch (PoE-Switch oder PoE-Injector) muss PoE liefern können. Endgerät muss PoE-fähig sein. Kabel mindestens Cat 5e, für hohe Wattagen Cat 6 oder besser.',
 '{"required_concepts": ["Strom + Daten über Ethernet", "802.3af 15W", "802.3at 30W PoE+", "802.3bt 60-90W", "PoE-Switch + Endgerät", "Cat 5e+"]}',
 NULL, 4, 'module-netzplan', 3, 240),

('cued',
 'Erkläre den Unterschied zwischen einem Access-Switch, Distribution-Switch und Core-Switch in einer 3-Layer-Architektur.',
 '3-Layer-Architektur (auch "hierarchisches Netzwerk-Design"):\n\n**Access-Layer** (auf Etagen, in Büros):\n- Verbindet Endgeräte (PCs, IP-Telefone, APs) mit dem Netzwerk\n- Viele Ports (24/48), günstig\n- L2-Switches mit PoE\n- Typisch: 100 Mbit/s oder 1 Gbit/s pro Port\n\n**Distribution-Layer** (Etagenverteiler / Verteiler-Schrank):\n- Aggregiert Access-Switches → bündelt Verbindungen\n- Inter-VLAN-Routing (deshalb meist Layer-3-fähig)\n- Implementiert Sicherheits-Policies, ACLs\n- Typisch: 10 Gbit/s zum Core, 1 Gbit/s zum Access\n\n**Core-Layer** (Rechenzentrum / Backbone):\n- Hochgeschwindigkeits-Backbone des Netzes\n- Verbindet Distribution-Switches untereinander + zum Internet/WAN\n- Layer-3, redundant ausgelegt (zwei Core-Switches mit HSRP/VRRP)\n- Typisch: 40/100 Gbit/s, keine ACLs (max. Performance)\n\nVorteil dieses Designs: Skalierung (man fügt nur Access-Switches hinzu, Core/Distribution bleiben stabil), klare Verantwortlichkeit, Fehler-Isolation.\n\nKleinere Unternehmen nutzen oft "Collapsed-Core" — Distribution + Core in einem Switch.',
 '{"required_concepts": ["Access Endgeräte 24/48 Ports", "Distribution Aggregation Inter-VLAN", "Core Backbone hochgeschwindig", "Skalierung", "Collapsed-Core Mittelstand"]}',
 NULL, 4, 'module-netzplan', 3, 240),

-- ============================================================
-- Spot-Check Pool (kurze Recall-Aufgaben)
-- ============================================================

('cued',
 'Auf welcher OSI-Schicht arbeitet ein Switch?',
 'Layer 2 (Sicherung) — leitet Frames anhand MAC-Adressen.',
 '{"required_concepts": ["L2", "MAC"]}',
 NULL, 1, 'module-netzplan-spot', 1, 30),

('cued',
 'Wie viele Subnetze trennt ein Router mit 3 Interfaces?',
 '3 Subnetze (eines pro Interface). Jedes Router-Interface bedient genau ein Subnetz.',
 '{"required_concepts": ["3", "Interface"]}',
 NULL, 1, 'module-netzplan-spot', 1, 30),

('cued',
 'Was ist die Hauptaufgabe einer DMZ?',
 'Pufferzone zwischen Internet und internem Netz. Enthält öffentlich erreichbare Server (Web/Mail/DNS), die bei Kompromittierung NICHT direkten Zugriff aufs interne LAN ermöglichen.',
 '{"required_concepts": ["Pufferzone", "öffentlich erreichbar", "kein direkter Zugriff LAN"]}',
 NULL, 2, 'module-netzplan-spot', 2, 60),

('cued',
 'Welcher PoE-Standard liefert bis zu 30 W?',
 'IEEE 802.3at (PoE+).',
 '{"required_concepts": ["802.3at", "PoE+"]}',
 NULL, 1, 'module-netzplan-spot', 1, 20),

('cued',
 'Was bedeutet "Trunk" zwischen zwei Switches?',
 'Eine Verbindung die mehrere VLANs gleichzeitig transportiert. Frames werden mit VLAN-Tags (IEEE 802.1Q) markiert.',
 '{"required_concepts": ["mehrere VLANs", "802.1Q", "Tag"]}',
 NULL, 2, 'module-netzplan-spot', 2, 45),

('cued',
 'Welcher aktuelle WLAN-Standard wird für moderne Büros empfohlen?',
 'IEEE 802.11ax (Wi-Fi 6) oder neuer 802.11be (Wi-Fi 7). Wi-Fi 6 ist der praktische Standard, Wi-Fi 7 für Zukunftssicherheit. Beide unterstützen WPA3-Verschlüsselung.',
 '{"required_concepts": ["802.11ax Wi-Fi 6", "WPA3"]}',
 NULL, 2, 'module-netzplan-spot', 2, 45),

('cued',
 'Welcher Switch-Typ kann routen und switchen gleichzeitig?',
 'Layer-3-Switch (L3-Switch). Kombiniert L2-Switching (MAC-basiertes Forwarding) mit L3-Routing (IP-basiertem Forwarding zwischen Subnetzen). Häufig im Distribution-Layer einer 3-Layer-Architektur.',
 '{"required_concepts": ["L3-Switch", "switchen + routen"]}',
 NULL, 1, 'module-netzplan-spot', 2, 45),

('cued',
 'Was ist der Vorteil einer zweistufigen DMZ gegenüber einer einstufigen?',
 'Zwei Firewalls hintereinander — Angreifer muss BEIDE überwinden. Defense in Depth, idealerweise verschiedene Hersteller, dann ist eine 0-Day-Lücke nicht in beiden Firewalls.',
 '{"required_concepts": ["Defense in Depth", "zwei Firewalls", "verschiedene Hersteller"]}',
 NULL, 2, 'module-netzplan-spot', 2, 60)

) AS v(item_type, prompt, model_answer,
       expected_answer_structure, grading_criteria, points, source_exam, difficulty, estimated_time_sec);

-- ============================================================
-- Items dem Modul zuordnen
-- ============================================================

WITH module_lookup AS (
    SELECT module_id FROM assessments.ap2_modules WHERE slug = 'netzplan-lesen' LIMIT 1
),
mastery_items AS (
    SELECT i.item_id, ROW_NUMBER() OVER (ORDER BY i.created_at) AS sort_order
    FROM assessments.ap2_learning_items i
    WHERE i.source_exam = 'module-netzplan'
)
INSERT INTO assessments.ap2_module_items (module_id, item_id, pool_tier, use_in, sort_order)
SELECT (SELECT module_id FROM module_lookup), m.item_id, 2, 'mastery', m.sort_order
FROM mastery_items m
ON CONFLICT (module_id, item_id) DO NOTHING;

WITH module_lookup AS (
    SELECT module_id FROM assessments.ap2_modules WHERE slug = 'netzplan-lesen' LIMIT 1
),
spotcheck_items AS (
    SELECT i.item_id, ROW_NUMBER() OVER (ORDER BY i.created_at) AS sort_order
    FROM assessments.ap2_learning_items i
    WHERE i.source_exam = 'module-netzplan-spot'
)
INSERT INTO assessments.ap2_module_items (module_id, item_id, pool_tier, use_in, sort_order)
SELECT (SELECT module_id FROM module_lookup), s.item_id, 1, 'spotcheck', s.sort_order
FROM spotcheck_items s
ON CONFLICT (module_id, item_id) DO NOTHING;

COMMIT;
