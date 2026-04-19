-- ============================================================================
-- Migration: 138_ap2_module_ipv6.sql
-- Description: Erstes Diagramm-Modul "IPv6-Konfiguration & Subnetting".
--              Lehrblock + Aufgaben-Pool (~30 Items, mehr folgen via 139+).
--
--              Mastery-Logik: 3× hintereinander ≥80% + Same-Day-Recall.
--              BW-spezifisch: Operatoren (Nennen/Berechnen/Bilden Sie).
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-04-19
-- ============================================================================

-- ============================================================================
-- Teil 1: Modul anlegen
-- ============================================================================

INSERT INTO assessments.ap2_modules
    (slug, name_de, name_en, description, theory_markdown,
     estimated_min, difficulty, sort_order, prerequisite_slugs, is_active)
VALUES (
    'ipv6-konfiguration',
    'IPv6 — Adressen, EUI-64, Subnetting',
    'IPv6 — Addressing, EUI-64, Subnetting',
    'Vollständiges IPv6-Modul für AP2 BW: Kurzform-Regeln, EUI-64 mit U/L-Bit-Flip, Subnetting mit Bit-Tabellen-Methode, Konfiguration aus Netzplan, Vergleich IPv4/IPv6.',
$theory$
## IPv6-Adressen — Grundlagen

Eine IPv6-Adresse ist **128 Bit** lang, geschrieben als 8 Gruppen à 16 Bit hexadezimal, getrennt durch Doppelpunkte:
`2001:0db8:00ea:2300:0000:0000:0000:0001/64`

### Kurzform-Regeln
1. **Führende Nullen** pro Gruppe weglassen: `0db8` → `db8`
2. **Längste zusammenhängende Null-Folge** durch `::` ersetzen — nur **EINMAL pro Adresse**.
3. Präfix-Länge mit `/n` dahinter.

Kurzform der Beispiel-Adresse: `2001:db8:ea:2300::1/64`

### Wichtige Adress-Präfixe
| Präfix | Bedeutung |
|---|---|
| `2000::/3` | Global Unicast (Internet-routbar) |
| `fe80::/10` | Link-Local (nur eigenes Subnetz, nicht routbar) |
| `fc00::/7` | Unique Local Address (privat, ähnlich RFC 1918) |
| `ff00::/8` | Multicast |
| `::1/128` | Loopback (entspricht `127.0.0.1`) |
| `::/128` | Unspecified |

---

## EUI-64 — Link-Local aus MAC-Adresse bilden

Aus einer MAC `DC:56:7B:F8:89:13` wird die Interface-ID einer Link-Local-Adresse so gebildet:

**Schritt 1** — MAC notieren (48 Bit):
`DC : 56 : 7B : F8 : 89 : 13`

**Schritt 2** — `FFFE` in die Mitte einfügen (zwischen 3. und 4. Oktett, ergibt 64 Bit):
`DC : 56 : 7B : FF : FE : F8 : 89 : 13`

**Schritt 3** — Das **siebte Bit** des ersten Oktetts invertieren (U/L-Bit-Flip):
`DC` = `1101 1100` → 7. Bit invertieren → `1101 1110` = `DE`
Ergebnis: `DE : 56 : 7B : FF : FE : F8 : 89 : 13`

**Schritt 4** — Präfix `fe80::/10` voranstellen:
`fe80::de56:7bff:fef8:8913/64`

Das ist die Link-Local-Adresse die das Interface ohne DHCP automatisch erhält (SLAAC).

---

## Subnetting — Bit-Tabellen-Methode

Ausgangslage: Provider gibt dir `2001:db8:cafe:2300::/56`.
Du brauchst z.B. 8 Subnetze.

**Schritt 1** — Wieviele Bits brauchst du? `2^n ≥ 8` → `n = 3 Bit`
**Schritt 2** — Neue CIDR: `56 + 3 = /59`
**Schritt 3** — Verbleibendes Oktett (`00`) binär aufteilen:

```
Subnetz | Bits     | Hex-Suffix | Adresse
─────────────────────────────────────────────
   0    | 000 0 0000 |    00    | 2001:db8:cafe:2300::/59
   1    | 001 0 0000 |    20    | 2001:db8:cafe:2320::/59
   2    | 010 0 0000 |    40    | 2001:db8:cafe:2340::/59
   3    | 011 0 0000 |    60    | 2001:db8:cafe:2360::/59
   4    | 100 0 0000 |    80    | 2001:db8:cafe:2380::/59
   5    | 101 0 0000 |    a0    | 2001:db8:cafe:23a0::/59
   6    | 110 0 0000 |    c0    | 2001:db8:cafe:23c0::/59
   7    | 111 0 0000 |    e0    | 2001:db8:cafe:23e0::/59
```

**Achtung Falle:** Hex-Sprung-Größe = `2^(8-Bits)` im letzten verwendeten Hex-Block.
Bei 3 Bits → Sprung `0x20` (= 32). Bei 5 Bits → Sprung `0x08` (= 8).

---

## Konfiguration eines Hosts aus Netzplan

Wenn der Netzplan zeigt:
- Router Link-Local: `fe80::1`
- DNS-Server Link-Local: `fe80::d`
- Subnetz Verwaltung: `2001:db8:ea:2301::/64`
- PC-Nummer in Suffix: `AB.1001`

Dann ist die Host-Konfiguration:
- Globale IPv6: `2001:db8:ea:2301::ab10:01/64`
- Default-Gateway: `fe80::1` (Link-Local des Routers — Standard für IPv6)
- DNS-Server: `fe80::d`

---

## IPv4 vs IPv6 — Kernunterschiede

| Aspekt | IPv4 | IPv6 |
|---|---|---|
| Adresslänge | 32 Bit | 128 Bit |
| Schreibweise | dezimal, `.` | hex, `:` |
| Konfiguration | DHCP / manuell | SLAAC, DHCPv6, manuell |
| Adressauflösung | ARP (Broadcast) | NDP / Neighbor Discovery (Multicast) |
| Header-Größe | variabel | feste 40 Byte |
| Sicherheit | optional | IPsec im Standard vorgesehen |
| NAT typisch | ja | nein (genug Adressen) |
| Broadcast | ja | nein → Multicast (`ff02::1` = alle Knoten) |
$theory$,
    14, 4, 1,
    '[]'::jsonb, TRUE
)
ON CONFLICT (slug) DO UPDATE SET
    name_de = EXCLUDED.name_de,
    description = EXCLUDED.description,
    theory_markdown = EXCLUDED.theory_markdown,
    estimated_min = EXCLUDED.estimated_min,
    difficulty = EXCLUDED.difficulty,
    sort_order = EXCLUDED.sort_order;

-- ============================================================================
-- Teil 2: Aufgaben in den Pool — als ap2_learning_items eintragen
-- ============================================================================

WITH topic_lookup AS (
    -- Wir hängen die Items an das bestehende ipv6-subnetting Topic
    SELECT topic_id FROM assessments.ap2_topics WHERE slug = 'ipv6-subnetting' LIMIT 1
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
-- Mastery-Pool: Kurzform / Adresstypen (Tier 1 — Einstieg)
-- ============================================================

('cued',
 'Schreibe die folgende IPv6-Adresse in Kurzform: 2001:0db8:0000:0000:0000:00ff:fe00:0001',
 'Kurzform: 2001:db8::ff:fe00:1\n\nRegeln angewendet:\n- Führende Nullen pro Gruppe weggelassen (0db8 → db8, 00ff → ff)\n- Längste Null-Folge (4 Gruppen) durch :: ersetzt\n- Präfix-Länge nicht angegeben weil keine im Beispiel war',
 '{"required_concepts": ["2001:db8::ff:fe00:1", "Doppelpunkt einmal", "führende Nullen weggelassen"]}',
 NULL, 3, 'module-ipv6', 2, 90),

('cued',
 'Welche der folgenden IPv6-Adressen ist eine Link-Local-Adresse? Begründe in einem Satz: a) 2001:db8::1  b) fe80::de56:7bff:fef8:8913  c) ff02::1  d) ::1',
 'b) fe80::de56:7bff:fef8:8913 ist eine Link-Local-Adresse, weil sie mit dem Präfix fe80::/10 beginnt. Link-Local-Adressen sind nur im eigenen Subnetz gültig (nicht routbar) und werden via SLAAC automatisch aus der MAC gebildet.\n\nDie anderen: a) Global Unicast (2000::/3), c) Multicast aller Knoten (ff00::/8), d) Loopback (::1).',
 '{"required_concepts": ["b", "fe80", "Link-Local", "nicht routbar"]}',
 NULL, 3, 'module-ipv6', 2, 90),

('cued',
 'Nenne den IPv6-Präfix für: a) Loopback  b) Multicast  c) Link-Local  d) Global Unicast',
 'a) Loopback: ::1/128 (nur eine Adresse, entspricht 127.0.0.1)\nb) Multicast: ff00::/8\nc) Link-Local: fe80::/10\nd) Global Unicast: 2000::/3',
 '{"required_concepts": ["::1/128", "ff00::/8", "fe80::/10", "2000::/3"]}',
 NULL, 4, 'module-ipv6', 2, 120),

('cued',
 'Erkläre den Unterschied zwischen einer Link-Local- und einer Global-Unicast-Adresse in IPv6.',
 'Link-Local (fe80::/10): nur im lokalen Subnetz gültig, nicht routbar, automatisch via SLAAC aus MAC-Adresse generiert. Jedes Interface hat IMMER eine Link-Local-Adresse, auch ohne Internet.\n\nGlobal Unicast (2000::/3): weltweit eindeutig + im Internet routbar. Wird vom Provider zugewiesen oder via SLAAC mit Provider-Präfix gebildet. Entspricht in der Funktion einer öffentlichen IPv4-Adresse.',
 '{"required_concepts": ["fe80::/10", "nicht routbar", "lokales Subnetz", "2000::/3", "Internet routbar", "weltweit eindeutig"]}',
 NULL, 4, 'module-ipv6', 3, 150),

-- ============================================================
-- Mastery-Pool: EUI-64 (Tier 2 — Standard)
-- ============================================================

('application',
 'Bilde die Link-Local-IPv6-Adresse aus der MAC-Adresse 00:1A:2B:3C:4D:5E nach dem EUI-64-Verfahren.\n\nGib alle vier Schritte einzeln an: (1) MAC notieren, (2) FFFE einfügen, (3) U/L-Bit invertieren, (4) Endergebnis mit fe80::/10-Präfix in Kurzform.',
 'Schritt 1 — MAC notieren:\n00:1A:2B:3C:4D:5E\n\nSchritt 2 — FFFE in die Mitte einfügen:\n00:1A:2B:FF:FE:3C:4D:5E\n\nSchritt 3 — Siebtes Bit des ersten Oktetts invertieren:\n00 = 0000 0000 → 7. Bit auf 1 setzen → 0000 0010 = 02\nErgebnis: 02:1A:2B:FF:FE:3C:4D:5E\n\nSchritt 4 — Mit fe80::/10-Präfix in Kurzform:\nfe80::21a:2bff:fe3c:4d5e/64',
 '{"required_concepts": ["FFFE einfügen", "00 wird 02", "U/L-Bit invertiert", "fe80::21a:2bff:fe3c:4d5e", "siebtes Bit"]}',
 '[{"criterion": "FFFE eingefügt", "weight": 2, "description": "zwischen 3. und 4. Oktett", "required": true},
   {"criterion": "U/L-Bit invertiert", "weight": 3, "description": "00 → 02", "required": true},
   {"criterion": "fe80::-Präfix vorangestellt", "weight": 2, "description": "korrekt", "required": true},
   {"criterion": "Kurzform korrekt", "weight": 2, "description": "fe80::21a:2bff:fe3c:4d5e/64", "required": true}]',
 9, 'module-ipv6', 4, 480),

('application',
 'Bilde die Link-Local-IPv6 aus der MAC AC:DE:48:23:45:67 nach EUI-64. Zeige alle 4 Schritte.',
 'Schritt 1: AC:DE:48:23:45:67\nSchritt 2: AC:DE:48:FF:FE:23:45:67\nSchritt 3: AC = 1010 1100 → 7. Bit flippen → 1010 1110 = AE\nErgebnis: AE:DE:48:FF:FE:23:45:67\nSchritt 4: fe80::acde:48ff:fe23:4567/64\n\nAnmerkung: Bei AC zu AE wird das 7. Bit von 0 auf 1 gesetzt — analog 02 zu 00 in der anderen Richtung.',
 '{"required_concepts": ["AC zu AE", "FFFE", "fe80::acde:48ff:fe23:4567/64"]}',
 '[{"criterion": "FFFE eingefügt", "weight": 2, "description": "korrekt", "required": true},
   {"criterion": "U/L-Bit korrekt", "weight": 3, "description": "AC → AE", "required": true},
   {"criterion": "Endergebnis Kurzform", "weight": 3, "description": "fe80::acde:48ff:fe23:4567/64", "required": true}]',
 8, 'module-ipv6', 4, 360),

('cued',
 'Was bewirkt das U/L-Bit-Flip in Schritt 3 des EUI-64-Verfahrens, und WELCHES Bit genau wird invertiert?',
 'Invertiert wird das **siebte Bit von links** im **ersten Oktett** (auch "Universal/Local-Bit" oder "U/L-Bit" genannt). Es zeigt an, ob die Interface-ID universell eindeutig ist (Bit = 1) oder lokal vergeben (Bit = 0).\n\nBei einer MAC-Adresse ist das U/L-Bit standardmäßig 0 (= universell verwaltet vom Hersteller). Im EUI-64-Format wird es invertiert auf 1 (= universell). Häufige Beispiele: 00 → 02, DC → DE, AC → AE, 12 → 10.\n\nFalle: NICHT das LSB (letztes Bit) invertieren — sondern das ZWEIT-niederwertigste Bit des FIRST-Oktetts.',
 '{"required_concepts": ["siebtes Bit", "erstes Oktett", "U/L-Bit", "00 zu 02", "Universal Local"]}',
 NULL, 4, 'module-ipv6', 4, 180),

-- ============================================================
-- Mastery-Pool: Subnetting (Tier 2-3 — Standard bis fortgeschritten)
-- ============================================================

('application',
 'Du hast vom Provider das Präfix 2001:db8:beef:1500::/56 bekommen. Du brauchst 8 Subnetze für verschiedene Abteilungen.\n\nGib an: (a) Anzahl benötigter Subnetz-Bits, (b) neue CIDR-Maske, (c) die 8 Subnetz-Adressen in der richtigen Reihenfolge.',
 '(a) 2^n ≥ 8 → n = 3 Bit\n(b) Neue CIDR: 56 + 3 = /59\n(c) Sprung-Größe im Hex: 2^(8-3) = 32 = 0x20\n\nDie 8 Subnetze:\n2001:db8:beef:1500::/59\n2001:db8:beef:1520::/59\n2001:db8:beef:1540::/59\n2001:db8:beef:1560::/59\n2001:db8:beef:1580::/59\n2001:db8:beef:15a0::/59\n2001:db8:beef:15c0::/59\n2001:db8:beef:15e0::/59',
 '{"required_concepts": ["3 Bit", "/59", "Sprung 0x20", "1500", "1520", "15e0"]}',
 '[{"criterion": "Bit-Anzahl korrekt", "weight": 2, "description": "3 Bit", "required": true},
   {"criterion": "Neue CIDR /59", "weight": 2, "description": "56 + 3", "required": true},
   {"criterion": "Sprung 32 erkannt", "weight": 2, "description": "0x20", "required": true},
   {"criterion": "8 Subnetze richtig", "weight": 4, "description": "alle 8 mit korrektem Suffix", "required": true}]',
 10, 'module-ipv6', 4, 600),

('application',
 'Provider-Präfix: 2001:db8:cafe:2300::/56. Du brauchst 16 Subnetze.\n\nNenne (a) Bit-Anzahl, (b) neue CIDR, (c) Hex-Sprung, (d) die ersten vier Subnetz-Adressen.',
 '(a) 2^n ≥ 16 → n = 4 Bit\n(b) Neue CIDR: 56 + 4 = /60\n(c) Sprung im Hex: 2^(8-4) = 16 = 0x10\n(d) Erste vier:\n2001:db8:cafe:2300::/60\n2001:db8:cafe:2310::/60\n2001:db8:cafe:2320::/60\n2001:db8:cafe:2330::/60',
 '{"required_concepts": ["4 Bit", "/60", "Sprung 0x10", "2300, 2310, 2320, 2330"]}',
 '[{"criterion": "4 Bit", "weight": 2, "description": "korrekt", "required": true},
   {"criterion": "/60 als neue CIDR", "weight": 2, "description": "korrekt", "required": true},
   {"criterion": "Sprung 16/0x10", "weight": 2, "description": "korrekt", "required": true},
   {"criterion": "4 Adressen", "weight": 3, "description": "alle korrekt", "required": true}]',
 9, 'module-ipv6', 4, 480),

('application',
 'Provider-Präfix: 2001:db8:beef:0100::/56. Du brauchst 64 Subnetze (z.B. für sehr granulare VLAN-Aufteilung).\n\nGib an: (a) Bit-Anzahl, (b) neue CIDR, (c) Hex-Sprung, (d) die ersten 4 und die letzten 2 Subnetz-Adressen.',
 '(a) 2^n ≥ 64 → n = 6 Bit\n(b) Neue CIDR: 56 + 6 = /62\n(c) Sprung im Hex: 2^(8-6) = 4 = 0x04\n\n(d) Erste vier:\n2001:db8:beef:0100::/62\n2001:db8:beef:0104::/62\n2001:db8:beef:0108::/62\n2001:db8:beef:010c::/62\n\nLetzte zwei:\n2001:db8:beef:01f8::/62\n2001:db8:beef:01fc::/62\n\nFiese Sache: Bei 6 Bits geht der Sprung über die hex-Block-Grenze hinweg — die ersten 2 Bits des 4. Hex-Blocks bleiben fix bei 01, der Rest variiert von 00 bis fc in 4er-Schritten.',
 '{"required_concepts": ["6 Bit", "/62", "Sprung 0x04", "0100, 0104, 0108, 010c", "01fc"]}',
 '[{"criterion": "Bit-Anzahl 6", "weight": 2, "description": "korrekt", "required": true},
   {"criterion": "/62 als CIDR", "weight": 2, "description": "korrekt", "required": true},
   {"criterion": "Sprung 0x04", "weight": 2, "description": "korrekt", "required": true},
   {"criterion": "Erste 4 Subnetze", "weight": 3, "description": "alle korrekt", "required": true},
   {"criterion": "Letzte 2 Subnetze", "weight": 2, "description": "01f8/01fc", "required": false}]',
 11, 'module-ipv6', 5, 720),

('application',
 'Provider-Präfix: 2001:db8:1234:5600::/56.\n\nWieviele /64-Subnetze sind insgesamt aus diesem /56 möglich, und wie lautet das letzte Subnetz?',
 'Verfügbare Bits zum Subnetting: 64 - 56 = 8 Bit.\nAnzahl Subnetze: 2^8 = 256.\n\nSprung im Hex: 2^(8-8) = 1 = 0x01.\n\nErstes Subnetz: 2001:db8:1234:5600::/64\nLetztes (256.) Subnetz: 2001:db8:1234:56ff::/64\n\nAlle Subnetze haben das Format 2001:db8:1234:56XX::/64 wobei XX von 00 bis ff durchläuft.',
 '{"required_concepts": ["256", "2^8", "5600", "56ff", "/64"]}',
 '[{"criterion": "256 Subnetze", "weight": 3, "description": "2^8 erkannt", "required": true},
   {"criterion": "Erstes + letztes Subnetz", "weight": 3, "description": "5600/56ff", "required": true}]',
 6, 'module-ipv6', 3, 360),

('cued',
 'Aus einem /48-Provider-Präfix sollen /64-Subnetze gebildet werden. Wieviele Subnetze sind möglich?',
 '64 - 48 = 16 Bit verfügbar zum Subnetting.\n2^16 = 65.536 Subnetze.\n\nDas reicht für ein sehr großes Unternehmen — Kundenpräfix /48 ist üblich für Geschäftskunden, /56 für Privatkunden.',
 '{"required_concepts": ["65536", "16 Bit", "2^16"]}',
 NULL, 3, 'module-ipv6', 2, 120),

-- ============================================================
-- Mastery-Pool: PC-Konfiguration aus Netzplan (Tier 3)
-- ============================================================

('application',
 'Du sollst den Admin-PC AB.1042 konfigurieren. Der Provider hat das Präfix 2001:db8:ea:2300::/56 zugeteilt. Im Verwaltungssubnetz wird /64 Nr. 1 verwendet (also :2300::). Aus dem Netzplan: Router-Link-Local fe80::1, DNS-Server-Link-Local fe80::d.\n\nGib für den Admin-PC die komplette IPv6-Konfiguration in Kurzform an: (a) globale IPv6-Adresse + Präfixlänge, (b) Default-Gateway, (c) DNS-Server.',
 '(a) Globale IPv6-Adresse:\n2001:db8:ea:2300::ab10:42/64\n(Die PC-Nummer AB.1042 wird als ab10:42 in die Interface-ID übernommen.)\n\n(b) Default-Gateway:\nfe80::1 (Link-Local des Routers — bei IPv6 üblich, weil Link-Local stabil bleibt auch bei Präfix-Wechsel)\n\n(c) DNS-Server:\nfe80::d',
 '{"required_concepts": ["2001:db8:ea:2300::ab10:42/64", "fe80::1", "fe80::d"]}',
 '[{"criterion": "Globale IPv6 mit PC-Nummer", "weight": 4, "description": "Suffix korrekt eingebaut", "required": true},
   {"criterion": "Gateway Link-Local", "weight": 2, "description": "fe80::1", "required": true},
   {"criterion": "DNS Link-Local", "weight": 2, "description": "fe80::d", "required": true},
   {"criterion": "Präfixlänge /64", "weight": 1, "description": "angegeben", "required": false}]',
 9, 'module-ipv6', 4, 420),

('application',
 'Provider-Präfix: 2001:db8:1234:5600::/56. Du sollst PC AB.0007 im WLAN-Subnetz konfigurieren — das ist /64 Nr. 3 (also :5602::). Router fe80::1, DNS fe80::d.\n\nGib komplette Konfig in Kurzform an.',
 'Globale IPv6: 2001:db8:1234:5602::ab00:07/64\nDefault-Gateway: fe80::1\nDNS-Server: fe80::d\n\nDie PC-Nummer AB.0007 wird in die Interface-ID übernommen (letzte 32 Bit).',
 '{"required_concepts": ["2001:db8:1234:5602::ab00:07/64", "fe80::1", "fe80::d"]}',
 '[{"criterion": "Subnetz korrekt", "weight": 2, "description": ":5602:", "required": true},
   {"criterion": "PC-Nummer im Suffix", "weight": 3, "description": "ab00:07", "required": true},
   {"criterion": "Gateway + DNS", "weight": 3, "description": "fe80::1 / fe80::d", "required": true}]',
 8, 'module-ipv6', 4, 360),

-- ============================================================
-- Mastery-Pool: IPv4 vs IPv6 Vergleich (Tier 2)
-- ============================================================

('cued',
 'Nenne 5 fundamentale Unterschiede zwischen IPv4 und IPv6.',
 '1. **Adresslänge**: IPv4 = 32 Bit (≈ 4,3 Mrd. Adressen), IPv6 = 128 Bit (≈ 3,4 × 10^38 Adressen).\n2. **Schreibweise**: IPv4 dezimal mit Punkten (192.168.1.1), IPv6 hexadezimal mit Doppelpunkten (2001:db8::1).\n3. **Adressauflösung**: IPv4 nutzt ARP (Broadcast L2), IPv6 nutzt NDP (Neighbor Discovery via Multicast).\n4. **Konfiguration**: IPv4 meist DHCP, IPv6 zusätzlich SLAAC (Stateless Address Autoconfiguration) — Hosts können sich ohne Server konfigurieren.\n5. **Broadcast vs Multicast**: IPv4 hat Broadcast (255.255.255.255), IPv6 nur Multicast (z.B. ff02::1 für alle Knoten im Link).\n\nWeitere Unterschiede: NAT bei IPv4 üblich, bei IPv6 nicht nötig; IPsec optional bei IPv4, im IPv6-Standard vorgesehen; Header-Größe variabel bei IPv4, fest 40 Byte bei IPv6.',
 '{"required_concepts": ["32 vs 128 Bit", "dezimal vs hex", "ARP vs NDP", "DHCP vs SLAAC", "Broadcast vs Multicast"]}',
 NULL, 5, 'module-ipv6', 3, 240),

('cued',
 'Was ist NDP (Neighbor Discovery Protocol) und was bei IPv4 das Pendant?',
 'NDP (Neighbor Discovery Protocol, RFC 4861) ist das IPv6-Pendant zu ARP. Aufgaben:\n- Auflösung IPv6-Adresse → MAC-Adresse (Neighbor Solicitation/Advertisement)\n- Router-Erkennung (Router Solicitation/Advertisement)\n- Präfix-Verteilung (Bestandteil von SLAAC)\n- Erreichbarkeitsprüfung (Neighbor Unreachability Detection)\n\nUnterschied zu ARP: NDP nutzt **ICMPv6-Multicast** (nicht Broadcast wie ARP). Multicast ist effizienter, weil nur das Ziel-Interface angesprochen wird (Solicited-Node-Multicast).\n\nGehört zu Layer 3 (Vermittlung), während ARP traditionell als Layer-2-Protokoll gilt.',
 '{"required_concepts": ["NDP", "ARP-Pendant", "ICMPv6-Multicast", "Solicited-Node", "SLAAC"]}',
 NULL, 4, 'module-ipv6', 3, 180),

('cued',
 'Was ist SLAAC und wie unterscheidet es sich von DHCPv6?',
 'SLAAC = Stateless Address Autoconfiguration. Ein Host bekommt seine globale IPv6-Adresse OHNE Server, nur mit Router-Hilfe:\n\n1. Host bildet Link-Local via EUI-64.\n2. Host sendet Router Solicitation (Multicast).\n3. Router antwortet mit Router Advertisement → Präfix /64.\n4. Host kombiniert Präfix + EUI-64 zur globalen Adresse.\n5. Doppelt-Adress-Erkennung (DAD) via Neighbor Solicitation.\n\nDHCPv6: Server-basiert wie DHCP unter IPv4 — vergibt zusätzlich DNS, NTP, Domain-Name etc.\n\nIn der Praxis oft kombiniert: SLAAC für Adresse, DHCPv6-stateless für DNS/NTP. Vorteil SLAAC: kein DHCP-Server nötig, weniger Single Point of Failure.',
 '{"required_concepts": ["Stateless Autoconfig", "ohne Server", "Router Advertisement", "EUI-64", "DHCPv6 für DNS"]}',
 NULL, 4, 'module-ipv6', 3, 180),

-- ============================================================
-- Spot-Check Pool (use_in='spotcheck' — kürzer für Recall)
-- ============================================================

('cued',
 'Wie viele /64-Subnetze passen in ein /56?',
 '2^(64-56) = 2^8 = 256 Subnetze.',
 '{"required_concepts": ["256", "2^8"]}',
 NULL, 1, 'module-ipv6-spot', 1, 30),

('cued',
 'Welcher Präfix kennzeichnet eine Link-Local-Adresse in IPv6?',
 'fe80::/10',
 '{"required_concepts": ["fe80::/10"]}',
 NULL, 1, 'module-ipv6-spot', 1, 20),

('cued',
 'Welches Bit wird beim EUI-64-Verfahren im ersten Oktett invertiert, und nach dem wievielten Schritt?',
 'Das siebte Bit von links (auch U/L-Bit oder "Universal/Local"-Bit) im ersten Oktett. Schritt 3 — nach dem Einfügen von FFFE.',
 '{"required_concepts": ["siebte Bit", "U/L-Bit", "Schritt 3"]}',
 NULL, 2, 'module-ipv6-spot', 2, 60),

('cued',
 'Was ist die Hex-Sprung-Größe wenn man /56 in 32 Subnetze teilt?',
 '32 = 2^5 → 5 Subnetz-Bits → neue CIDR /61.\nHex-Sprung = 2^(8-5) = 8 = 0x08.\nSubnetze gehen also 00, 08, 10, 18, 20, ..., f8.',
 '{"required_concepts": ["0x08", "Sprung 8", "/61"]}',
 NULL, 2, 'module-ipv6-spot', 3, 90),

('cued',
 'Aus MAC 02:00:00:00:00:01 — welche Link-Local-Adresse ergibt sich?',
 'Schritt 1: 02:00:00:00:00:01\nSchritt 2: 02:00:00:FF:FE:00:00:01\nSchritt 3: 02 = 0000 0010 → 7. Bit invertieren → 0000 0000 = 00\nSchritt 4: fe80::00:00ff:fe00:1 → in Kurzform fe80::ff:fe00:1/64',
 '{"required_concepts": ["fe80::ff:fe00:1", "02 zu 00", "FFFE"]}',
 NULL, 3, 'module-ipv6-spot', 3, 120),

('cued',
 'Was ist das IPv6-Pendant zu ARP?',
 'NDP (Neighbor Discovery Protocol) — nutzt ICMPv6-Multicast statt Broadcast.',
 '{"required_concepts": ["NDP", "Neighbor Discovery"]}',
 NULL, 1, 'module-ipv6-spot', 2, 30),

('cued',
 'Was bedeutet die IPv6-Adresse ::1?',
 'Loopback-Adresse — entspricht 127.0.0.1 in IPv4. Verweist auf das eigene Interface.',
 '{"required_concepts": ["Loopback", "127.0.0.1"]}',
 NULL, 1, 'module-ipv6-spot', 1, 30),

('cued',
 'In welchem Bereich liegen Multicast-Adressen in IPv6?',
 'ff00::/8 — alle Adressen die mit ff beginnen sind Multicast. Wichtige Beispiele: ff02::1 = alle Knoten, ff02::2 = alle Router auf dem Link.',
 '{"required_concepts": ["ff00::/8", "ff02::1"]}',
 NULL, 2, 'module-ipv6-spot', 2, 60)

) AS v(item_type, prompt, model_answer,
       expected_answer_structure, grading_criteria, points, source_exam, difficulty, estimated_time_sec);

-- ============================================================================
-- Teil 3: Items dem Modul zuordnen via ap2_module_items
-- ============================================================================

WITH module_lookup AS (
    SELECT module_id FROM assessments.ap2_modules WHERE slug = 'ipv6-konfiguration' LIMIT 1
),
mastery_items AS (
    SELECT i.item_id, ROW_NUMBER() OVER (ORDER BY i.created_at) AS sort_order
    FROM assessments.ap2_learning_items i
    WHERE i.source_exam = 'module-ipv6'
),
spotcheck_items AS (
    SELECT i.item_id, ROW_NUMBER() OVER (ORDER BY i.created_at) AS sort_order
    FROM assessments.ap2_learning_items i
    WHERE i.source_exam = 'module-ipv6-spot'
)
INSERT INTO assessments.ap2_module_items (module_id, item_id, pool_tier, use_in, sort_order)
SELECT (SELECT module_id FROM module_lookup), m.item_id, 2, 'mastery', m.sort_order
FROM mastery_items m
ON CONFLICT (module_id, item_id) DO NOTHING;

WITH module_lookup AS (
    SELECT module_id FROM assessments.ap2_modules WHERE slug = 'ipv6-konfiguration' LIMIT 1
),
spotcheck_items AS (
    SELECT i.item_id, ROW_NUMBER() OVER (ORDER BY i.created_at) AS sort_order
    FROM assessments.ap2_learning_items i
    WHERE i.source_exam = 'module-ipv6-spot'
)
INSERT INTO assessments.ap2_module_items (module_id, item_id, pool_tier, use_in, sort_order)
SELECT (SELECT module_id FROM module_lookup), s.item_id, 1, 'spotcheck', s.sort_order
FROM spotcheck_items s
ON CONFLICT (module_id, item_id) DO NOTHING;

COMMIT;
