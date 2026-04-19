-- ============================================================================
-- Migration: 144_ap2_ipv6_deep.sql
-- Description: IPv6 Modul Deep-Build — 12 Sub-Areas gemappt,
--              bestehende 17 Items getaggt, ~42 neue Items ergänzt
--              für ein vollständiges IPv6-Kern-Modul (~59 Items total).
--
--              Sub-Areas: basics, notation, comparison, address-types,
--              eui64, autoconfig, prefix, ndp, netzplan, transition,
--              security, troubleshoot.
--
--              Primäres Aufgaben-Format: BW-IHK-Operatoren (Nennen/Erklären/
--              Berechnen/Vergleichen Sie). Inspiriert von AP1-2026 BW + den
--              letzten 10 AP2-BW-Jahrgängen.
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-04-19
-- ============================================================================

-- ============================================================================
-- Teil 1: Sub-Area Meta (Labels, Icons, Sortierung für die Heatmap)
-- ============================================================================

INSERT INTO assessments.ap2_module_sub_area_meta
    (module_id, sub_area, label_de, label_en, sort_order, icon, color, description)
SELECT m.module_id, v.sub_area, v.label_de, v.label_en, v.sort_order, v.icon, v.color, v.description
FROM assessments.ap2_modules m
CROSS JOIN (VALUES
    ('basics',        'Grundlagen',             'Basics',             10,  '📘', '#3b82f6',
     'Warum IPv6, Adress-Raum, Geschichte, 128-Bit-Struktur.'),
    ('notation',      'Notation & Kürzung',     'Notation',           20,  '✏️', '#8b5cf6',
     'Langform/Kurzform, Doppel-Doppelpunkt-Regeln, führende Nullen.'),
    ('comparison',    'IPv4 ↔ IPv6',            'IPv4 vs IPv6',       30,  '🔀', '#ec4899',
     'Unterschiede: Adresslänge, Header, NAT, Broadcast/Multicast, NDP, IPsec.'),
    ('address-types', 'Adress-Typen',           'Address Types',      40,  '🏷️', '#f59e0b',
     'Global Unicast, Link-Local, ULA, Multicast, Loopback, Unspecified.'),
    ('eui64',         'EUI-64 & U/L-Bit',       'EUI-64',             50,  '🔑', '#14b8a6',
     'Interface-ID aus MAC, FFFE-Einschub, 7. Bit invertieren, Privacy Extensions.'),
    ('autoconfig',    'SLAAC & DHCPv6',         'SLAAC / DHCPv6',     60,  '⚙️', '#06b6d4',
     'Stateless Address Autoconfig, Router Advertisement, DHCPv6 stateful/stateless.'),
    ('prefix',        'Präfix & Subnetting',    'Prefix calc',        70,  '📐', '#a855f7',
     'Präfix aus ISP zerlegen, Subnetze bilden, Hex-Nibble-Rechnung.'),
    ('ndp',           'Neighbor Discovery',     'NDP',                80,  '📡', '#6366f1',
     'NDP ersetzt ARP: NS/NA, RS/RA, Duplicate Address Detection.'),
    ('netzplan',      'IPv6 aus Netzplan',      'From network plan',  90,  '🗺️', '#f97316',
     'Klausurstil: PC-Nr + Präfix → vollständige IPv6-Konfiguration.'),
    ('transition',    'IPv4→IPv6 Übergang',     'Transition',        100,  '🌉', '#84cc16',
     'Dual-Stack, 6to4, 6in4-Tunneling, NAT64, DNS64.'),
    ('security',      'Sicherheit & IPsec',     'Security',          110,  '🔐', '#ef4444',
     'IPsec-Pflichtfunktion, AH vs ESP, Firewall-Regeln für IPv6.'),
    ('troubleshoot',  'Troubleshooting',        'Troubleshoot',      120,  '🔍', '#64748b',
     'ping6, tracert6, ipconfig /all, ip -6 route, ND-Tabelle prüfen.')
) AS v(sub_area, label_de, label_en, sort_order, icon, color, description)
WHERE m.slug = 'ipv6-konfiguration'
ON CONFLICT (module_id, sub_area) DO UPDATE SET
    label_de = EXCLUDED.label_de,
    label_en = EXCLUDED.label_en,
    sort_order = EXCLUDED.sort_order,
    icon = EXCLUDED.icon,
    color = EXCLUDED.color,
    description = EXCLUDED.description;

-- ============================================================================
-- Teil 2: Bestehende Items taggen (Pattern-Match auf prompt)
-- ============================================================================

-- Helper: nur Items aus dem IPv6-Modul-Pool taggen
-- (source_exam = 'module-ipv6' oder 'module-ipv6-pt2')

UPDATE assessments.ap2_learning_items
SET sub_area = 'notation'
WHERE source_exam LIKE 'module-ipv6%'
  AND sub_area IS NULL
  AND (prompt ILIKE '%Kurzform%' OR prompt ILIKE '%Langform%'
       OR prompt ILIKE '%führende Null%' OR prompt ILIKE '%Doppelpunkt%');

UPDATE assessments.ap2_learning_items
SET sub_area = 'address-types'
WHERE source_exam LIKE 'module-ipv6%'
  AND sub_area IS NULL
  AND (prompt ILIKE '%Link-Local%' OR prompt ILIKE '%Global Unicast%'
       OR prompt ILIKE '%Multicast%' OR prompt ILIKE '%Loopback%'
       OR prompt ILIKE '%fe80%' OR prompt ILIKE '%ULA%'
       OR prompt ILIKE '%Präfix für%' OR prompt ILIKE '%Adress-Typ%'
       OR prompt ILIKE '%Adresstyp%');

UPDATE assessments.ap2_learning_items
SET sub_area = 'eui64'
WHERE source_exam LIKE 'module-ipv6%'
  AND sub_area IS NULL
  AND (prompt ILIKE '%EUI-64%' OR prompt ILIKE '%EUI64%'
       OR prompt ILIKE '%MAC-Adresse%' OR prompt ILIKE '%U/L-Bit%'
       OR prompt ILIKE '%FFFE%' OR prompt ILIKE '%invertier%');

UPDATE assessments.ap2_learning_items
SET sub_area = 'autoconfig'
WHERE source_exam LIKE 'module-ipv6%'
  AND sub_area IS NULL
  AND (prompt ILIKE '%SLAAC%' OR prompt ILIKE '%DHCPv6%'
       OR prompt ILIKE '%Autokonfiguration%' OR prompt ILIKE '%Router Advertisement%');

UPDATE assessments.ap2_learning_items
SET sub_area = 'prefix'
WHERE source_exam LIKE 'module-ipv6%'
  AND sub_area IS NULL
  AND (prompt ILIKE '%Subnetting%' OR prompt ILIKE '%/64%'
       OR prompt ILIKE '%/48%' OR prompt ILIKE '%/56%'
       OR prompt ILIKE '%Subnetz-ID%' OR prompt ILIKE '%wie viele Subnetze%'
       OR prompt ILIKE '%wie viele Host%');

UPDATE assessments.ap2_learning_items
SET sub_area = 'netzplan'
WHERE source_exam LIKE 'module-ipv6%'
  AND sub_area IS NULL
  AND (prompt ILIKE '%Netzplan%' OR prompt ILIKE '%Admin-PC%'
       OR prompt ILIKE '%Bestimme die IPv6%' OR prompt ILIKE '%DNS-Server%'
       OR prompt ILIKE '%Gateway%');

UPDATE assessments.ap2_learning_items
SET sub_area = 'comparison'
WHERE source_exam LIKE 'module-ipv6%'
  AND sub_area IS NULL
  AND (prompt ILIKE '%Unterschied%IPv4%' OR prompt ILIKE '%IPv4 vs IPv6%'
       OR prompt ILIKE '%IPv4 und IPv6%' OR prompt ILIKE '%vergleich%IPv%');

-- Rest als 'basics' taggen
UPDATE assessments.ap2_learning_items
SET sub_area = 'basics'
WHERE source_exam LIKE 'module-ipv6%'
  AND sub_area IS NULL;

-- ============================================================================
-- Teil 3: ~42 neue Items einfügen
-- ============================================================================

WITH topic_lookup AS (
    SELECT topic_id FROM assessments.ap2_topics
     WHERE slug = 'ipv6-subnetting' LIMIT 1
)
INSERT INTO assessments.ap2_learning_items
    (topic_id, item_type, prompt, model_answer, expected_answer_structure,
     grading_criteria, points, source_exam, difficulty, estimated_time_sec,
     sub_area, tags)
SELECT (SELECT topic_id FROM topic_lookup), v.item_type, v.prompt, v.model_answer,
       v.expected_answer_structure::jsonb, v.grading_criteria::jsonb,
       v.points, v.source_exam, v.difficulty, v.estimated_time_sec,
       v.sub_area, v.tags::text[]
FROM (VALUES

-- ============================================================
-- SUB-AREA: basics (4 items)
-- ============================================================

('cued',
 'Nennen Sie 3 Gründe warum IPv6 IPv4 ablöst.',
 '1. Adress-Erschöpfung: IPv4 hat nur ~4,3 Mrd. Adressen (2^32), IPv6 hat 2^128 ≈ 3,4 × 10^38 — praktisch unbegrenzt.\n2. Kein NAT mehr nötig: Jedes Gerät kann eine öffentliche Adresse haben (bessere End-to-End-Konnektivität, einfacheres Troubleshooting).\n3. Plug-and-Play über SLAAC: Geräte konfigurieren sich ohne DHCP-Server selbst aus Router Advertisements + EUI-64.',
 '{"required_concepts": ["Adress-Erschöpfung", "128 Bit", "NAT", "SLAAC"]}',
 NULL, 3, 'module-ipv6', 2, 90,
 'basics', ARRAY['klausur-standard']),

('cued',
 'Wie viele Bits hat eine IPv6-Adresse und wie wird sie geschrieben?',
 '128 Bit, notiert als 8 Gruppen à 16 Bit hexadezimal, getrennt durch Doppelpunkte. Beispiel: 2001:0db8:85a3:0000:0000:8a2e:0370:7334.',
 '{"required_concepts": ["128 Bit", "8 Gruppen", "16 Bit", "hexadezimal", "Doppelpunkt"]}',
 NULL, 2, 'module-ipv6', 1, 60,
 'basics', ARRAY['grundlagen']),

('cued',
 'Was ist der Unterschied zwischen unicast, multicast und anycast in IPv6?',
 'Unicast: 1-zu-1, genau ein Empfänger (wie bei IPv4).\nMulticast: 1-zu-viele, Präfix ff00::/8, alle Mitglieder der Gruppe empfangen das Paket gleichzeitig. Ersetzt IPv4-Broadcast.\nAnycast: 1-zu-nächster, mehrere Hosts haben dieselbe Adresse, geroutet wird zum topologisch nächsten (z.B. für CDNs, DNS-Root-Server).',
 '{"required_concepts": ["Unicast", "Multicast", "Anycast", "ff00::/8", "nächster", "ersetzt Broadcast"]}',
 NULL, 3, 'module-ipv6', 3, 120,
 'basics', ARRAY['grundlagen', 'operator-unterscheiden']),

('cued',
 'Warum gibt es in IPv6 keinen Broadcast mehr und womit wurde er ersetzt?',
 'Broadcast erzeugt CPU-Last auf ALLEN Geräten im Segment (auch wenn sie das Paket nicht brauchen). IPv6 ersetzt Broadcast durch gezieltes Multicast mit gut definierten Gruppen:\n- ff02::1 (all-nodes) — alle Knoten im Link\n- ff02::2 (all-routers) — nur Router\n- ff02::1:ffXX:XXXX (solicited-node) — Geräte mit gleichem letzten 24-Bit-Suffix (für NDP statt ARP)\n\nVorteil: Hosts verwerfen Multicast auf NIC-Ebene wenn sie nicht in der Gruppe sind → weniger Interrupts.',
 '{"required_concepts": ["Broadcast entfällt", "Multicast", "ff02::1", "all-nodes", "solicited-node"]}',
 NULL, 4, 'module-ipv6', 3, 150,
 'basics', ARRAY['grundlagen', 'operator-erklaeren']),

-- ============================================================
-- SUB-AREA: notation (3 neue, existing haben schon 2-3)
-- ============================================================

('cued',
 'Schreibe die IPv6-Adresse fe80:0000:0000:0000:0000:0000:0000:0001 in Kurzform und begründe jede angewendete Regel.',
 'Kurzform: fe80::1\n\nAngewendete Regeln:\n1. Führende Nullen pro Gruppe weggelassen (0000 → weg bei leerer Gruppe).\n2. Längste zusammenhängende Null-Folge (hier 6 Gruppen) durch :: ersetzt — nur EINMAL pro Adresse erlaubt.\n3. Letzte Gruppe 0001 → 1 (führende Nullen).',
 '{"required_concepts": ["fe80::1", "führende Nullen", "längste Null-Folge", "Doppel-Doppelpunkt nur einmal"]}',
 NULL, 3, 'module-ipv6', 2, 90,
 'notation', ARRAY['klausur-standard']),

('cued',
 'Warum ist 2001::db8::1 eine UNGÜLTIGE IPv6-Kurzform und wie schreibt man sie korrekt?',
 'UNGÜLTIG weil :: zweimal vorkommt — dann wäre nicht mehr eindeutig bestimmbar, wie viele Nullen jeweils gemeint sind. Die Regel erlaubt den Doppel-Doppelpunkt nur EINMAL pro Adresse.\n\nKorrekt wäre z.B.: 2001:0:0:0:db8::1 (nur die rechte Null-Folge gekürzt) ODER 2001::db8:0:0:0:1 (nur die linke).',
 '{"required_concepts": ["Doppelpunkt nur einmal", "nicht eindeutig", "2001:0:0:0:db8::1"]}',
 NULL, 3, 'module-ipv6', 3, 120,
 'notation', ARRAY['klausur-trick', 'operator-begruenden']),

('cued',
 'Schreibe die IPv6-Adresse 2001:db8::c:0:0:0:1 in Langform mit allen Nullen.',
 'Langform: 2001:0db8:000c:0000:0000:0000:0000:0001\n\nDas :: stand zwischen db8 und c für 0 Gruppen (weil rechts schon 4 Gruppen stehen: 0, 0, 0, 1). Also müssen wir NUR die vorhandenen Gruppen mit führenden Nullen auffüllen.\n\nVorsicht: Hier ist :: gar keine Null-Expansion, sondern nur "db8::c" = "db8:0:0:0:c" wäre falsch interpretiert. Die richtige Lesart: 2001 + db8 + :: + c + 0 + 0 + 0 + 1 = 8 Gruppen total.',
 '{"required_concepts": ["2001:0db8:000c:0000:0000:0000:0000:0001", "auf 4 Stellen auffüllen", "8 Gruppen"]}',
 NULL, 3, 'module-ipv6', 4, 150,
 'notation', ARRAY['klausur-trick']),

-- ============================================================
-- SUB-AREA: comparison (7 items — der große Vergleichs-Block)
-- ============================================================

('cued',
 'Nennen Sie 3 Unterschiede zwischen IPv4 und IPv6.',
 '1. Adresslänge: IPv4 = 32 Bit (dezimal, 4 Oktette), IPv6 = 128 Bit (hexadezimal, 8 Gruppen).\n2. Kein NAT in IPv6: Adress-Raum so groß, dass jedes Gerät eine öffentliche Adresse haben kann.\n3. Broadcast (IPv4) → Multicast (IPv6): ff02::1 = alle Knoten, keine CPU-Last mehr bei Nicht-Empfängern.\n\n(Weitere mögliche: IPsec in IPv6 Pflicht / optional in IPv4; ARP (IPv4) → NDP (IPv6); DHCP (IPv4) → SLAAC+DHCPv6 (IPv6); Fragmentierung nur beim Sender in IPv6; Header IPv6 hat feste 40 Byte ohne Checksumme.)',
 '{"required_concepts": ["32 Bit vs 128 Bit", "NAT", "Broadcast", "Multicast", "ff02::1"]}',
 NULL, 3, 'module-ipv6', 2, 90,
 'comparison', ARRAY['klausur-standard', 'operator-nennen']),

('cued',
 'Erläutern Sie den Unterschied zwischen ARP (IPv4) und NDP (IPv6).',
 'ARP (IPv4): Broadcast-basiert. "Wer hat IP 192.168.1.5?" geht an alle Hosts, jedes Gerät muss es prüfen und ggf. verwerfen.\n\nNDP (IPv6, Neighbor Discovery Protocol): Multicast-basiert auf der solicited-node-Gruppe (ff02::1:ffXX:XXXX, letzte 24 Bit der Ziel-IP). Nur Geräte mit passendem Suffix empfangen es. Zusätzlich macht NDP über ICMPv6-Nachrichten auch Router-Discovery (RS/RA), Redirect und Duplicate Address Detection.\n\nKurzform: ARP ist beschränkt auf MAC-Auflösung + Broadcast; NDP ist IPv6-nativ, effizienter und kann mehr.',
 '{"required_concepts": ["ARP Broadcast", "NDP Multicast", "solicited-node", "ICMPv6", "DAD"]}',
 NULL, 4, 'module-ipv6', 4, 180,
 'comparison', ARRAY['klausur-standard', 'operator-erlaeutern']),

('cued',
 'Warum ist in IPv6 NAT normalerweise nicht mehr nötig?',
 'NAT wurde bei IPv4 eingeführt, weil der 32-Bit-Adress-Raum (~4,3 Mrd.) nicht für alle Geräte im Internet reicht. NAT spart Adressen, indem mehrere private IPs hinter EINER öffentlichen versteckt werden.\n\nIPv6 hat 2^128 ≈ 3,4 × 10^38 Adressen — genug für jedes Sandkorn auf der Erde. Jedes Gerät bekommt eine eigene öffentliche (Global Unicast) Adresse. Vorteile:\n- End-to-End-Konnektivität (einfacheres Troubleshooting, bessere P2P)\n- Keine NAT-Tabellen auf Routern\n- Bessere Sicherheit in Protokollen die NAT schlecht unterstützen (z.B. IPsec Tunnel mit AH)\n\nFür Interne Privatsphäre gibt es ULA (fc00::/7) und Privacy Extensions (RFC 4941).',
 '{"required_concepts": ["NAT wegen Adress-Erschöpfung", "2^128", "Global Unicast", "End-to-End", "ULA als Privatbereich"]}',
 NULL, 4, 'module-ipv6', 4, 180,
 'comparison', ARRAY['klausur-standard', 'operator-begruenden']),

('cued',
 'Vergleichen Sie die Fragmentierung von Paketen zwischen IPv4 und IPv6.',
 'IPv4: Router DÜRFEN fragmentieren wenn MTU zu klein. Empfänger setzt Fragmente wieder zusammen. Felder im Header: Identification, Flags (DF, MF), Fragment Offset.\n\nIPv6: Nur der SENDER fragmentiert — via Path MTU Discovery (PMTUD) über ICMPv6 "Packet Too Big". Router DÜRFEN NICHT fragmentieren (Performance-Grund). Fragmentierung liegt in einem optionalen Extension Header.\n\nVorteil IPv6: Router haben weniger Arbeit. Nachteil: ICMPv6 PMTUD muss durchgelassen werden (häufig fälschlich per Firewall geblockt — bricht IPv6 dann).',
 '{"required_concepts": ["IPv4 Router fragmentiert", "IPv6 nur Sender", "PMTUD", "ICMPv6 Packet Too Big", "Extension Header"]}',
 NULL, 4, 'module-ipv6', 4, 180,
 'comparison', ARRAY['klausur-advanced', 'operator-vergleichen']),

('cued',
 'Welche Rolle spielt DHCP in IPv4 vs IPv6?',
 'IPv4: DHCP ist Standard für Host-Konfiguration (IP, Subnetz, Gateway, DNS). Gerät startet mit 0.0.0.0 und fordert per Broadcast Konfiguration an (DHCPDISCOVER→OFFER→REQUEST→ACK).\n\nIPv6: Zwei Wege parallel:\n1. SLAAC (Stateless Address Autoconfiguration): Host hört auf Router Advertisements, baut sich die Adresse selbst aus Präfix (vom Router) + Interface-ID (EUI-64 oder zufällig). KEIN DHCP-Server nötig für die Adresse.\n2. DHCPv6: Kann stateful sein (Server verwaltet alle Adressen wie IPv4-DHCP) oder stateless (nur zusätzliche Info wie DNS-Server, während SLAAC die Adresse macht).\n\nFaustregel: Heim/Small-LAN = SLAAC reicht. Unternehmen mit Adress-Management-Bedarf = DHCPv6 stateful.',
 '{"required_concepts": ["IPv4 DHCP", "IPv6 SLAAC", "DHCPv6 stateful/stateless", "Router Advertisement"]}',
 NULL, 4, 'module-ipv6', 3, 180,
 'comparison', ARRAY['klausur-standard', 'operator-vergleichen']),

('cued',
 'Ist IPsec in IPv4 oder IPv6 vorgeschrieben? Erläutern Sie.',
 'IPsec war im ORIGINAL-IPv6-RFC (2460) als Pflichtfunktion vorgeschrieben — jede IPv6-Implementierung MUSS IPsec unterstützen. Später (RFC 6434, 2011) wurde das auf SHOULD herabgestuft, aber praktisch unterstützen fast alle IPv6-Stacks IPsec nativ.\n\nIPv4: IPsec ist optional, wird als separate Protokoll-Erweiterung aufgesetzt.\n\nIn der Klausur: Wenn nach "Pflichtfunktion in IPv6" gefragt — IPsec antworten (auch wenn der Status inzwischen SHOULD ist, die Klausurbücher sagen meist noch Pflicht).',
 '{"required_concepts": ["IPv6 Pflicht (historisch)", "IPv4 optional", "AH / ESP", "Transport / Tunnel"]}',
 NULL, 3, 'module-ipv6', 3, 120,
 'comparison', ARRAY['klausur-standard', 'operator-erlaeutern']),

('cued',
 'Unterscheiden Sie die Header-Struktur IPv4 und IPv6.',
 'IPv4-Header: variabel 20-60 Byte, 14 Felder inkl. Checksumme, Options-Feld, Fragmentation-Felder.\n\nIPv6-Header: FEST 40 Byte, 8 Felder (Version, Traffic Class, Flow Label, Payload Length, Next Header, Hop Limit, Source, Destination). KEINE Checksumme (Checksumme wird von Layer 2/4 übernommen — schneller weiter-routing). Optionen werden per Extension Header angehängt (Hop-by-Hop, Routing, Fragment, Destination, AH, ESP).\n\nVorteil IPv6: Router muss nur fixe 40 Byte parsen → schneller. Keine Checksumme-Neuberechnung bei jedem Hop nötig.',
 '{"required_concepts": ["40 Byte fest", "keine Checksumme", "Extension Header", "Flow Label", "schneller Routing"]}',
 NULL, 4, 'module-ipv6', 4, 180,
 'comparison', ARRAY['klausur-advanced', 'operator-unterscheiden']),

-- ============================================================
-- SUB-AREA: address-types (3 neue)
-- ============================================================

('cued',
 'Was ist eine Unique Local Address (ULA), welcher Präfix und wozu dient sie?',
 'ULA: Adressbereich für PRIVATE, nicht ins Internet routbare IPv6-Adressen — die Entsprechung zu RFC-1918 bei IPv4 (10.x, 172.16.x, 192.168.x).\n\nPräfix: fc00::/7, wobei das 8. Bit (L-Bit) gesetzt sein muss → praktisch genutzt wird fd00::/8 (locally assigned).\n\nAufbau: fd + 40 zufällige Bit (Global ID, sollte zufällig generiert werden damit Firmen sich nicht überschneiden) + 16 Bit Subnet ID + 64 Bit Interface ID.\n\nBeispiel: fd12:3456:789a::1/64\n\nEinsatz: Intern-Netzwerk ohne Internet, redundantes Second-Network, VPN-Infrastruktur.',
 '{"required_concepts": ["ULA", "fc00::/7", "fd00::/8", "nicht routbar", "Ersatz für RFC 1918"]}',
 NULL, 3, 'module-ipv6', 3, 150,
 'address-types', ARRAY['klausur-advanced']),

('cued',
 'Nennen Sie die wichtigsten IPv6-Multicast-Gruppen und ihren Zweck.',
 'ff01::1 — Node-local All-Nodes (innerhalb eines Interfaces)\nff02::1 — Link-local All-Nodes (alle Geräte im Segment — ersetzt IPv4-Broadcast)\nff02::2 — Link-local All-Routers (nur Router auf dem Segment — für RS)\nff02::1:ff00:0/104 — Solicited-Node-Multicast (Suffix = letzte 24 Bit der Ziel-IP, für NDP statt ARP)\nff02::5 — OSPFv3 All-Routers\nff02::6 — OSPFv3 Designated Router\nff02::9 — RIPng\nff02::d — PIM-Router\n\nSkopus-Präfix: ff0X wobei X = Scope (1=node, 2=link, 5=site, 8=org, e=global).',
 '{"required_concepts": ["ff02::1 all-nodes", "ff02::2 routers", "solicited-node ff02::1:ff", "Scope"]}',
 NULL, 4, 'module-ipv6', 4, 180,
 'address-types', ARRAY['klausur-advanced', 'operator-nennen']),

('cued',
 'Erklären Sie was die IPv6-Adresse :: bedeutet und wo sie verwendet wird.',
 ':: ist die "Unspecified Address" (::/128) — ALLE 128 Bit sind 0. Sie entspricht 0.0.0.0 in IPv4.\n\nVerwendung:\n- Als Quell-Adresse bevor ein Host selbst eine Adresse hat (z.B. bei Duplicate Address Detection, DAD).\n- Als Socket-Bind-Adresse um "auf allen Interfaces lauschen" zu signalisieren.\n- NIEMALS als Ziel-Adresse — ein Paket an :: würde verworfen.\n\nNicht zu verwechseln mit ::1 (Loopback, analog zu 127.0.0.1).',
 '{"required_concepts": ["Unspecified Address", "0.0.0.0", "DAD", "nie als Ziel", "Unterschied zu ::1"]}',
 NULL, 3, 'module-ipv6', 3, 120,
 'address-types', ARRAY['klausur-standard', 'operator-erklaeren']),

-- ============================================================
-- SUB-AREA: eui64 (3 neue)
-- ============================================================

('cued',
 'Warum wird beim EUI-64-Verfahren das 7. Bit des ersten Oktetts invertiert (U/L-Bit-Flip)?',
 'Das 7. Bit (U/L-Bit, "Universal/Local") in einer MAC-Adresse unterscheidet:\n- 0 = vom Hersteller vergeben (universell eindeutig, aus IEEE-OUI)\n- 1 = lokal administriert (z.B. manuell gesetzt)\n\nIEEE-Standard MACs haben typisch U/L=0. Für EUI-64 wird das Bit INVERTIERT auf 1 gesetzt, um zu signalisieren "das ist eine EUI-64 Interface-ID, abgeleitet aus einer globalen MAC". Dadurch bleibt die Eindeutigkeit erhalten und die Interface-ID ist klar erkennbar als auto-generiert.\n\nPraxis: Bit 7 des ersten Oktetts umkippen. DC (11011100) → DE (11011110) — nur das siebte Bit ändert sich (von 0 auf 1).',
 '{"required_concepts": ["7. Bit", "Universal/Local", "0 Hersteller", "1 lokal", "Invertierung = EUI-64 Kennzeichen"]}',
 NULL, 4, 'module-ipv6', 4, 180,
 'eui64', ARRAY['klausur-standard', 'operator-begruenden']),

('application',
 'Bilde aus der MAC-Adresse 00:1A:2B:3C:4D:5E die Link-Local-Adresse per EUI-64 (zeige alle Schritte).',
 'Schritt 1 — MAC in 48 Bit notieren:\n00:1A:2B:3C:4D:5E\n\nSchritt 2 — FFFE in die Mitte einfügen (zwischen 3. und 4. Oktett):\n00:1A:2B:FF:FE:3C:4D:5E\n\nSchritt 3 — 7. Bit des ersten Oktetts invertieren:\n00 = 0000 0000 → 02 = 0000 0010 (Bit 7 von 0 auf 1)\n→ 02:1A:2B:FF:FE:3C:4D:5E\n\nSchritt 4 — Präfix fe80::/10 voranstellen, In IPv6-Format umwandeln:\nfe80::021A:2BFF:FE3C:4D5E\n\nSchritt 5 — Kurzform (führende Nullen weg):\nfe80::21a:2bff:fe3c:4d5e',
 '{"required_concepts": ["FFFE in Mitte", "7. Bit flip", "00 → 02", "fe80::", "fe80::21a:2bff:fe3c:4d5e"]}',
 NULL, 6, 'module-ipv6', 4, 300,
 'eui64', ARRAY['klausur-rechnung', 'operator-bilden']),

('cued',
 'Was sind Privacy Extensions (RFC 4941) und warum wurden sie eingeführt?',
 'Problem bei EUI-64: Die Interface-ID enthält die MAC-Adresse → jede IPv6-Adresse eines Geräts ist weltweit eindeutig einem physischen Gerät zuordenbar. Tracking-Risiko.\n\nPrivacy Extensions: Host generiert zusätzlich zu EUI-64 eine zweite, ZUFÄLLIGE Interface-ID. Diese wird als Absender für ausgehende Verbindungen genutzt (temporär, z.B. alle 24 h wechselnd). Die EUI-64-Adresse bleibt für eingehende Verbindungen.\n\nAktivierung: Windows und modern-Linux/macOS standardmäßig an. Deaktiviert per: `netsh interface ipv6 set privacy disabled` (Windows).',
 '{"required_concepts": ["Tracking wegen MAC", "zufällige Interface-ID", "temporäre Adressen", "RFC 4941"]}',
 NULL, 3, 'module-ipv6', 3, 120,
 'eui64', ARRAY['klausur-advanced']),

-- ============================================================
-- SUB-AREA: autoconfig (3 neue)
-- ============================================================

('cued',
 'Beschreiben Sie den Ablauf von SLAAC in 4 Schritten.',
 '1. Host sendet per Multicast Router Solicitation (RS) an ff02::2 (all-routers) — „Welcher Router ist hier?"\n2. Router antwortet mit Router Advertisement (RA) an ff02::1 (all-nodes) mit:\n   - Präfix (z.B. 2001:db8:1::/64)\n   - Default Gateway (die Link-Local des Routers, z.B. fe80::1)\n   - DNS (in neueren RAs optional, RDNSS-Option)\n   - M-Flag (DHCPv6 nötig?) / O-Flag (weitere Info per DHCPv6?)\n3. Host bildet seine globale Adresse aus Präfix + Interface-ID (EUI-64 oder zufällig).\n4. Host führt Duplicate Address Detection (DAD) durch — sendet Neighbor Solicitation an seine eigene Adresse, wenn niemand antwortet → Adresse wird aktiviert.\n\nKein DHCP-Server nötig — Router ist die Quelle.',
 '{"required_concepts": ["RS ff02::2", "RA ff02::1", "Präfix", "Interface-ID", "DAD"]}',
 NULL, 4, 'module-ipv6', 3, 180,
 'autoconfig', ARRAY['klausur-standard', 'operator-beschreiben']),

('cued',
 'Wann wird stateless DHCPv6 und wann stateful DHCPv6 benutzt?',
 'Stateless DHCPv6: Host holt sich Adresse über SLAAC (vom Router), aber ZUSÄTZLICH per DHCPv6 nur noch Extras wie DNS-Server-Adresse oder NTP. Der DHCPv6-Server verwaltet keine Adressen.\n\nStateful DHCPv6: Wie IPv4-DHCP — Server vergibt die IPv6-Adresse aus einem Pool und merkt sich welche Adresse an welche DUID gebunden ist. Für Umgebungen wo genaue Adress-Kontrolle nötig ist (z.B. DNS-Registrierung, Audit).\n\nWer entscheidet? Die M- und O-Flags im Router Advertisement:\n- M=0, O=0 → nur SLAAC, kein DHCPv6\n- M=0, O=1 → SLAAC + stateless DHCPv6 (für DNS etc.)\n- M=1, O=1 → stateful DHCPv6 (voller Modus, Router liefert nur Präfix-Info, Adresse kommt vom DHCPv6-Server)',
 '{"required_concepts": ["stateless", "stateful", "M-Flag", "O-Flag", "DUID"]}',
 NULL, 4, 'module-ipv6', 4, 180,
 'autoconfig', ARRAY['klausur-advanced']),

('cued',
 'Was ist Duplicate Address Detection (DAD) und wie funktioniert sie?',
 'DAD: Pflicht-Prüfung bei IPv6 — bevor ein Host eine Adresse aktiviert, muss er sicherstellen dass niemand sie schon hat.\n\nAblauf:\n1. Host bildet Kandidat-Adresse (z.B. per SLAAC).\n2. Status = tentative.\n3. Host sendet Neighbor Solicitation (NS) an die solicited-node-Multicast-Gruppe der Kandidat-Adresse, mit Ziel-Adresse = Kandidat, Absender = :: (unspecified).\n4. Wartet 1 Sekunde (DupAddrDetectTransmits, RFC 4862).\n5. Wenn keine Neighbor Advertisement (NA) kommt → Adresse ist frei → Status = preferred.\n6. Wenn NA kommt → Adresse bereits vergeben → Status = duplicate, Adresse wird verworfen, Fehler geloggt.',
 '{"required_concepts": ["tentative", "Neighbor Solicitation", "Absender ::", "1 Sekunde warten", "preferred / duplicate"]}',
 NULL, 3, 'module-ipv6', 4, 150,
 'autoconfig', ARRAY['klausur-advanced', 'operator-beschreiben']),

-- ============================================================
-- SUB-AREA: prefix (4 neue)
-- ============================================================

('application',
 'Ein ISP teilt dir das Präfix 2001:0db8:00ea:2300::/56 zu. Wie viele /64-Subnetze kannst du bilden und wie sieht das erste und letzte aus?',
 'Rechnung: /56 → /64 sind 64-56 = 8 Bit für Subnetz-ID → 2^8 = 256 Subnetze.\n\nDie Subnetz-ID sitzt in der 4. Gruppe (Bit 57-64), die 2300 + 8 variable Bit.\n\nErstes Subnetz: 2001:db8:ea:2300::/64 (Subnetz-ID = 0x00)\nZweites:         2001:db8:ea:2301::/64 (ID = 0x01)\n...\nLetztes:         2001:db8:ea:23ff::/64 (ID = 0xff)\n\nMerken: /56 → 256 /64-Netze; /48 → 65536 /64-Netze (Standard für Firmen-Allokation).',
 '{"required_concepts": ["256 Subnetze", "2^8", "2001:db8:ea:2300::/64", "2001:db8:ea:23ff::/64"]}',
 '{"calculator_hint": {"model": "Casio FX-991DE X", "mode": "COMP (MODE 1)", "formula": "2^(64 - prefix)", "example": "2^(64-56) = 2^8 = 256", "steps": [{"label": "2 eingeben", "keys": "2"}, {"label": "Hoch-Taste", "keys": "^"}, {"label": "Exponent eingeben", "keys": "8"}, {"label": "Ausführen", "keys": "=", "display": "256"}]}}',
 8, 'module-ipv6', 4, 360,
 'prefix', ARRAY['klausur-rechnung', 'operator-berechnen']),

('application',
 'Berechne: ISP gibt 2001:db8::/48 — du willst 10 Standorte mit je 4 VLANs versorgen, jedes VLAN als /64. Wieviele Subnetz-Bits brauchst du pro Standort und welches Präfix teilst du den Standorten zu?',
 'Benötigt: pro Standort 4 /64 → 2 Bit Subnetz-ID innerhalb des Standorts (2^2 = 4 Subnetze).\n\nFür 10 Standorte brauchst du ceil(log2(10)) = 4 Bit (2^4 = 16, reicht für 10).\n\nGesamt: /48 + 4 Bit für Standort + 2 Bit für VLAN = /54 pro Standort. Besser: /52 pro Standort (12 Bit für Subnetz-ID intern, genug Reserve für Wachstum).\n\nStandort 1: 2001:db8:0000::/52\nStandort 2: 2001:db8:1000::/52\n...\nVLAN 1 in Standort 1: 2001:db8:0000::/64\nVLAN 2 in Standort 1: 2001:db8:0001::/64\n\nFaustregel: Immer großzügig zuteilen — Präfixe sind keine Mangelware in IPv6.',
 '{"required_concepts": ["4 Bit für 10 Standorte", "2 Bit für 4 VLANs", "/52 pro Standort", "2001:db8:0000::/52"]}',
 '{"calculator_hint": {"model": "Casio FX-991DE X", "mode": "COMP (MODE 1)", "formula": "benötigte Bits = ceil(log2(N))", "example": "log2(10) = 3.32 → 4 Bit", "steps": [{"label": "log eingeben (Basis 10)", "keys": "log", "display": "log("}, {"label": "Argument 10", "keys": "1 0 )", "display": "log(10)"}, {"label": "÷ log(2)", "keys": "÷ log ( 2 )", "display": "log(10)÷log(2)"}, {"label": "Ausführen", "keys": "=", "display": "3.3219..."}], "note": "Aufrunden auf ganzzahlig → 4 Bit"}}',
 10, 'module-ipv6', 5, 600,
 'prefix', ARRAY['klausur-rechnung', 'operator-berechnen', 'mehrstufig']),

('cued',
 'Wieso bekommen Endkunden von ISPs typisch ein /56 oder /48 und nicht nur ein /64?',
 'Ein /64 wäre nur EIN Subnetz. Endkunden brauchen aber meist mehrere (LAN, WLAN, Gäste-WLAN, IoT, DMZ, VoIP). RFC 6177 empfiehlt:\n- Privathaushalte: /56 (256 /64-Subnetze, genug für alle Heimgeräte + Gäste + Smart-Home)\n- Kleinunternehmen: /56 oder /48\n- Mittelstand: /48 (65.536 /64-Subnetze)\n- Große Firmen: /32 bis /40\n\nDie Adressen sind so reichlich, dass Sparen keinen Sinn macht — ein /48 hat mehr Adressen als das gesamte IPv4-Internet. Sparsamkeit macht Routing-Tabellen nur komplizierter.',
 '{"required_concepts": ["/64 = nur 1 Subnetz", "/56 = 256", "/48 = 65536", "RFC 6177", "Routing-Einfachheit"]}',
 NULL, 3, 'module-ipv6', 3, 120,
 'prefix', ARRAY['klausur-standard', 'operator-begruenden']),

('application',
 'Das ISP-Präfix 2001:0db8:00ea:2300::/56 soll in 8 Gleich-Subnetze für 8 Abteilungen zerlegt werden. Gib alle 8 Präfixe an.',
 '/56 zerlegen in 8 Teile = 3 Bit dazu (2^3 = 8) → /59 pro Abteilung.\n\nDie 8 Subnetz-IDs der 3. Bit-Position sitzen im 4. Gruppen-Byte nach dem festen 2300:\nBinary der letzten 16 Bit nach Präfix: 0010 0011 XXXX XXXX (23 fest, rest variabel)\nMit 3 Bit Sub: 0010 0011 000 / 001 / 010 / ... / 111 + 5 offene\n\nAlso die 8 Präfixe:\n1. 2001:db8:ea:2300::/59\n2. 2001:db8:ea:2320::/59\n3. 2001:db8:ea:2340::/59\n4. 2001:db8:ea:2360::/59\n5. 2001:db8:ea:2380::/59\n6. 2001:db8:ea:23a0::/59\n7. 2001:db8:ea:23c0::/59\n8. 2001:db8:ea:23e0::/59\n\nSchrittweite in Hex: 0x20 (weil 3 Bit weiter links im letzten Nibble).',
 '{"required_concepts": ["/59", "Schritt 0x20", "2001:db8:ea:2300::/59", "2001:db8:ea:23e0::/59", "3 Bit"]}',
 '{"calculator_hint": {"model": "Casio FX-991DE X", "mode": "BASE-N (MODE 4 → HEX)", "formula": "Schritt = 2^(64 - neuer_prefix_ohne_vorhandene_bits), in Hex pro Nibble", "example": "Für /59 aus /56: 3 Bit Schritt → 0x20 im letzten Nibble vor Interface-ID-Teil", "steps": [{"label": "MODE → 4 für BASE-N", "keys": "MODE 4"}, {"label": "HEX-Modus", "keys": "x² (=HEX)"}, {"label": "2^5 eingeben", "keys": "2 x^y 5 ="}, {"label": "Ergebnis als Hex lesen", "display": "20"}]}}',
 10, 'module-ipv6', 5, 600,
 'prefix', ARRAY['klausur-rechnung', 'operator-bilden']),

-- ============================================================
-- SUB-AREA: ndp (4 items)
-- ============================================================

('cued',
 'Was ist das Neighbor Discovery Protocol (NDP) und welche ICMPv6-Typen gehören dazu?',
 'NDP: IPv6-Protokoll für Nachbar-Beziehungen auf einem Link — ersetzt bei IPv6 das ARP sowie Teile von ICMP und IGMP.\n\nDie 5 Haupt-Nachrichten (alle ICMPv6):\n- Type 133: Router Solicitation (RS) — „Welcher Router ist hier?"\n- Type 134: Router Advertisement (RA) — Router antwortet + broadcastet periodisch\n- Type 135: Neighbor Solicitation (NS) — „Wer hat Adresse X?" (ARP-Ersatz) + DAD\n- Type 136: Neighbor Advertisement (NA) — „Ich habe X, hier meine MAC"\n- Type 137: Redirect — „Für Ziel Y geh direkt zu Gateway Z"\n\nWird OFT in Firewalls fälschlich geblockt → IPv6 bricht.',
 '{"required_concepts": ["NDP", "RS 133", "RA 134", "NS 135", "NA 136", "Redirect 137", "ICMPv6"]}',
 NULL, 4, 'module-ipv6', 4, 180,
 'ndp', ARRAY['klausur-advanced', 'operator-nennen']),

('cued',
 'Erläutern Sie wie NDP ARP ersetzt — am Beispiel „Host A will Host B erreichen".',
 'IPv4/ARP: A sendet Broadcast „Wer hat 192.168.1.5?" → ALLE Hosts empfangen, nur B antwortet → A hat Bs MAC.\n\nIPv6/NDP: A sendet Neighbor Solicitation an die solicited-node-Multicast-Gruppe der Ziel-Adresse. Diese Gruppe wird aus den letzten 24 Bit der Ziel-IPv6 gebildet: ff02::1:ff + letzte 6 Hex-Stellen der Ziel-Adresse.\n\nBeispiel: B hat 2001:db8::1234:5678. Die solicited-node-Group ist ff02::1:ff34:5678.\n\nNur Geräte deren letzte 24 Bit ebenfalls 34:5678 enden, empfangen das NS (auf NIC-Ebene gefiltert per Multicast-MAC-Mapping). In der Praxis ist das fast immer nur B → NS erreicht nur B, B antwortet mit NA, A hat Bs MAC. Weniger CPU-Last, bessere Skalierung.',
 '{"required_concepts": ["solicited-node", "ff02::1:ff", "letzte 24 Bit", "NIC-Filtering", "weniger CPU als ARP"]}',
 NULL, 4, 'module-ipv6', 4, 210,
 'ndp', ARRAY['klausur-advanced', 'operator-erlaeutern']),

('cued',
 'Welche Gefahren bringt NDP mit sich — und wie schützt man sich?',
 'Gefahren:\n1. RA-Spoofing: Ein Angreifer sendet gefälschte Router Advertisements → leitet allen Traffic auf sich um (MITM).\n2. NS/NA-Spoofing: Angreifer gibt vor eine andere IP zu haben (analog zu ARP-Spoofing).\n3. DoS via zu vielen NS: Gerät ist überlastet mit Neighbor-Cache-Updates.\n\nSchutz:\n- RA Guard auf Switch-Port (blockiert RAs auf Access-Ports, erlaubt nur auf Uplink zum Router).\n- DHCPv6 Snooping — Switch merkt sich welche Ports legitime DHCPv6-Server haben.\n- SEND (Secure Neighbor Discovery, RFC 3971) — kryptografisch signierte NDP-Nachrichten (aber kaum deployed).\n- Auf Endgerät: NDP-Rate-Limiting in Kernel-Stack.',
 '{"required_concepts": ["RA-Spoofing", "NS-Spoofing", "RA Guard", "DHCPv6 Snooping", "SEND"]}',
 NULL, 3, 'module-ipv6', 4, 180,
 'ndp', ARRAY['klausur-security']),

('cued',
 'Was steht in der Neighbor-Cache-Tabelle eines IPv6-Hosts?',
 'Wie bei ARP-Cache, aber strukturierter. Pro Eintrag:\n- IPv6-Adresse des Nachbarn\n- MAC-Adresse (Link-Layer Address)\n- Status:\n  * INCOMPLETE — NS gesendet, keine Antwort noch\n  * REACHABLE — NA bekommen, Adresse gültig (ca. 30 Sek)\n  * STALE — Timer abgelaufen, vor nächster Verwendung prüfen\n  * DELAY / PROBE — aktive Prüfung läuft\n- Interface-Index\n- Router-Flag (ist dieser Nachbar auch Router?)\n\nAuf Linux einsehbar mit: `ip -6 neigh show`\nAuf Windows: `netsh interface ipv6 show neighbors`',
 '{"required_concepts": ["Neighbor Cache", "INCOMPLETE / REACHABLE / STALE", "ip -6 neigh", "MAC", "Router-Flag"]}',
 NULL, 3, 'module-ipv6', 3, 150,
 'ndp', ARRAY['klausur-advanced', 'troubleshoot']),

-- ============================================================
-- SUB-AREA: netzplan (4 neue — AP1-2026-Klausurstil)
-- ============================================================

('application',
 'Laut Netzplan: Admin-PC Nr. AB.1001, Netz-Präfix 2001:0db8:00ea:2301::/64, Router-Link-Local fe80::1, DNS-Server Link-Local fe80::d. Gib vollständige IPv6-Konfiguration für den Admin-PC in Kurzform an — globale Adresse, Gateway, DNS, Präfix.',
 'Vollständige Konfiguration:\n\nGlobale IPv6-Adresse: 2001:db8:ea:2301::ab:1001/64\n(Die PC-Nr. AB.1001 wird in die Interface-ID eingebaut, Rest mit Null-Folge gekürzt.)\n\nGateway: fe80::1\n(In IPv6 ist das Gateway STANDARD-MÄSSIG die Link-Local-Adresse des Routers — nicht die globale!)\n\nDNS-Server: fe80::d\n(Ebenfalls Link-Local — so wie es im Netzplan steht.)\n\nPräfixlänge: /64\n\nAlternativ würde bei echter Netzplan-Aufgabe der Pfad auch bei 2001:db8:ea:2301::1001 liegen wenn die Herkunft der PC-Nr. anders interpretiert wird — die AP-Musterlösung nimmt meist die direkt eingesetzte Nr.',
 '{"required_concepts": ["2001:db8:ea:2301::ab:1001/64", "Gateway fe80::1", "DNS fe80::d", "/64", "Link-Local für Gateway"]}',
 NULL, 8, 'module-ipv6', 4, 420,
 'netzplan', ARRAY['klausur-ap1-2026', 'klausur-standard']),

('application',
 'Ein zweites WLAN-Subnetz soll auf 2001:0db8:00ea:2302::/64 laufen. Benenne eine gültige IPv6-Adresse für den Access-Point und für einen WLAN-Client.',
 'AP-Adresse (z.B. erste in /64): 2001:db8:ea:2302::1/64\n\nClient-Adresse (frei wählbar in /64):\n- Per SLAAC via EUI-64: 2001:db8:ea:2302:xxxx:xxff:fexx:xxxx (aus MAC)\n- Manuell: z.B. 2001:db8:ea:2302::100/64\n- Per DHCPv6-Server: beliebig im Pool\n\nWichtig: Beide Geräte müssen im gleichen /64 sein, sonst kein lokaler Link → Router wird fälschlich angefragt.',
 '{"required_concepts": ["2001:db8:ea:2302::1/64", "2001:db8:ea:2302::100/64", "gleiches /64", "SLAAC alternativ"]}',
 NULL, 3, 'module-ipv6', 3, 120,
 'netzplan', ARRAY['klausur-standard', 'operator-benennen']),

('cued',
 'Warum ist für das WLAN ein eigenes Subnetz sinnvoll, obwohl technisch alles in /56 reinpassen würde?',
 'Gründe:\n1. Isolation — Broadcast-Domain getrennt; WLAN-Probleme kontaminieren nicht das LAN.\n2. Sicherheit — WLAN ist inhärent unsicherer (physikalischer Zugriff möglich); Firewall-Regel „WLAN darf nur ins Internet, nicht ins Admin-LAN" einfach zu setzen.\n3. QoS / Traffic-Shaping — WLAN-Traffic (VoIP, Video-Call) kann priorisiert werden.\n4. SSID-spezifische Policies — Gäste-SSID im eigenen /64.\n5. Skalierbarkeit — eigenes Subnetz = eigene Default-Gateway-Adresse → klarere Troubleshooting-Pfade.',
 '{"required_concepts": ["Isolation", "Sicherheit", "Firewall-Regeln", "QoS", "Skalierbarkeit"]}',
 NULL, 2, 'module-ipv6', 3, 120,
 'netzplan', ARRAY['klausur-ap1-2026', 'operator-begruenden']),

('cued',
 'Welche Informationen muss ein Router per Router Advertisement senden damit ein Client via SLAAC korrekt konfiguriert ist?',
 'Minimum:\n1. Präfix (z.B. 2001:db8:ea:2301::/64) mit A-Flag=1 (autonom) und L-Flag=1 (on-link).\n2. Default-Gateway — implizit die Quell-Adresse des RA (Link-Local des Routers, z.B. fe80::1).\n3. Hop Limit (typ. 64).\n4. MTU (optional aber empfohlen, z.B. 1500 für Ethernet, 1280 Minimum IPv6).\n5. RDNSS (DNS-Server, RFC 8106, optional aber empfohlen) — z.B. fe80::d.\n6. M-Flag (DHCPv6 nötig für Adresse?) und O-Flag (DHCPv6 nötig für Extras?).\n\nOhne das reicht dem Client: Präfix + Router-Link-Local → er bildet Adresse + Route selbst.',
 '{"required_concepts": ["Präfix", "A-Flag / L-Flag", "Gateway = RA-Quelle", "RDNSS für DNS", "M/O-Flag"]}',
 NULL, 4, 'module-ipv6', 4, 210,
 'netzplan', ARRAY['klausur-advanced']),

-- ============================================================
-- SUB-AREA: transition (4 items)
-- ============================================================

('cued',
 'Was ist Dual-Stack und warum ist es der häufigste IPv6-Rollout-Weg?',
 'Dual-Stack: Gerät/Router hat GLEICHZEITIG einen kompletten IPv4- und einen IPv6-Stack und kann Pakete in beiden Protokollen senden/empfangen. DNS entscheidet (A-Record = IPv4, AAAA-Record = IPv6).\n\nWarum beliebt:\n- Keine Migration „in einer Nacht" nötig — alte IPv4-Dienste laufen weiter, neue IPv6-Dienste kommen dazu.\n- Volle Kompatibilität: Host A erreicht IPv4-nur Host B wie gehabt; Host A erreicht IPv6-nur Host C nativ.\n- DNS64 + NAT64 als Optionen falls Peer nur IPv6 hat.\n\nNachteil: Doppelte Pflege von Routing, Firewall-Regeln, Monitoring. Ressourcen-Aufwand.',
 '{"required_concepts": ["Dual-Stack", "IPv4 + IPv6 parallel", "DNS A / AAAA", "schrittweise Migration", "doppelter Aufwand"]}',
 NULL, 3, 'module-ipv6', 2, 120,
 'transition', ARRAY['klausur-standard', 'operator-erklaeren']),

('cued',
 'Wozu dient 6in4-Tunneling und wann setzt man es ein?',
 '6in4: IPv6-Pakete werden in IPv4-Pakete eingepackt (IPv4-Protokoll-Nr. 41) und über reine IPv4-Netze transportiert. Ideal für:\n- Unternehmen mit IPv6-Insel, aber IPv4-nur-ISP → Tunnel zum IPv6-Gateway-Provider (z.B. Hurricane Electric tunnelbroker.net).\n- Zwei Standorte mit IPv6, dazwischen IPv4-nur-WAN.\n\nAblauf: IPv6-Host → eigener Router packt IPv6-Paket in IPv4 ein → Paket durch IPv4-Netz → Tunnel-Endpunkt entpackt → IPv6 geht nativ weiter.\n\nAlternative: 6to4 (automatischer Tunnel, Präfix 2002::/16) — ist aber deprecated, NAT-Probleme, schlecht routbar.',
 '{"required_concepts": ["6in4", "IPv4 Protokoll 41", "Tunnel", "Hurricane Electric", "6to4 deprecated"]}',
 NULL, 3, 'module-ipv6', 4, 150,
 'transition', ARRAY['klausur-advanced']),

('cued',
 'Was ist NAT64 + DNS64 und wann braucht man es?',
 'Szenario: Client hat NUR IPv6, will aber IPv4-nur-Dienst erreichen (z.B. Website ohne AAAA-Record).\n\nDNS64: DNS-Server synthetisiert AAAA-Records aus vorhandenen A-Records. Die IPv4-Adresse wird in einen speziellen IPv6-Präfix (Standard: 64:ff9b::/96) eingebettet.\nBeispiel: A-Record 93.184.216.34 → synthetisches AAAA: 64:ff9b::5db8:d822\n\nNAT64: Router sieht Paket an 64:ff9b::/96, extrahiert die eingebetteten IPv4-Bits, übersetzt das IPv6-Paket in IPv4 und sendet ins IPv4-Internet. Antworten werden umgekehrt übersetzt.\n\nEinsatz: IPv6-only Netze (moderne Handy-Mobilfunk-Netze, Enterprise-Netze die Kosten sparen wollen). Problem: Protokolle die IP-Adressen im Payload transportieren (FTP aktiv, SIP) brauchen ALGs.',
 '{"required_concepts": ["NAT64", "DNS64", "64:ff9b::/96", "IPv4 in IPv6 eingebettet", "IPv6-only Netze"]}',
 NULL, 4, 'module-ipv6', 4, 180,
 'transition', ARRAY['klausur-advanced']),

('cued',
 'Was ist eine IPv4-mapped IPv6-Adresse und wo wird sie benutzt?',
 'Format: ::ffff:A.B.C.D — die ersten 80 Bit 0, dann 16 Bit 1 (ffff), dann 32 Bit IPv4-Adresse in dezimaler Punkt-Notation.\n\nBeispiel: 192.168.1.1 → ::ffff:192.168.1.1 oder ::ffff:c0a8:0101\n\nEinsatz: Dual-Stack-Sockets im Betriebssystem. Eine Applikation die NUR IPv6 kann, empfängt trotzdem IPv4-Verbindungen durch das OS — der eingehende IPv4-Peer erscheint als IPv4-mapped IPv6-Adresse im `accept()`-Call. Transparent.\n\nAchtung: Niemals über die Leitung schicken — nur OS-intern für Socket-API-Kompatibilität. Firewalls sollten sie nicht akzeptieren.',
 '{"required_concepts": ["::ffff:IPv4", "OS-intern", "Dual-Stack-Sockets", "nicht über Netz senden"]}',
 NULL, 3, 'module-ipv6', 4, 150,
 'transition', ARRAY['klausur-advanced']),

-- ============================================================
-- SUB-AREA: security (3 items)
-- ============================================================

('cued',
 'Welche IPsec-Protokolle gibt es und was ist der Unterschied zwischen AH und ESP?',
 'Zwei Teil-Protokolle:\n\nAH (Authentication Header, IP-Protokoll 51):\n- Nur Integrität + Authentizität (Absender beweisbar, Inhalt nicht verändert)\n- KEINE Verschlüsselung\n- Funktioniert nicht mit NAT (weil NAT den Header ändert, HMAC zerbricht)\n\nESP (Encapsulating Security Payload, IP-Protokoll 50):\n- Verschlüsselung + optional Integrität + Authentizität\n- KANN mit NAT funktionieren (NAT-Traversal via UDP 4500)\n- Standard in fast allen VPN-Implementierungen\n\nBeide Modi:\n- Transport: nur Payload geschützt, IP-Header sichtbar — für Host-to-Host\n- Tunnel: komplettes Paket inkl. Original-IP-Header neu gewrapt — für Site-to-Site VPN',
 '{"required_concepts": ["AH 51", "ESP 50", "AH ohne Verschlüsselung", "Transport vs Tunnel", "AH + NAT = Problem"]}',
 NULL, 4, 'module-ipv6', 4, 180,
 'security', ARRAY['klausur-standard', 'operator-unterscheiden']),

('cued',
 'Welche Firewall-Regeln muss man für IPv6 typisch ZUSÄTZLICH zu IPv4 pflegen?',
 'IPv6 bringt eigene Protokoll-Ebenen:\n\n1. ICMPv6 — NICHT pauschal blocken! Teile sind lebensnotwendig:\n   - Type 1 (Destination Unreachable)\n   - Type 2 (Packet Too Big — PMTUD)\n   - Type 3 (Time Exceeded)\n   - Type 4 (Parameter Problem)\n   - Type 128/129 (Echo Request/Reply für ping6)\n   - Type 133-137 (NDP — MUSS durchgelassen werden)\n   - Type 143 (MLDv2)\n\n2. Extension Headers: Firewall muss sie dekodieren können (manche alte Geräte hängen sich auf bei unbekannten Extensions).\n\n3. Multicast-Regeln: ff02-Adressen lokal erlauben.\n\n4. Spezielle Adressen blockieren aus Internet: ::, ::1, fe80::/10, ff00::/8, 2001:db8::/32 (Dokumentations-Präfix).',
 '{"required_concepts": ["ICMPv6 nicht pauschal blocken", "NDP durchlassen", "Extension Headers", "Multicast-Regeln", "fe80 von extern blocken"]}',
 NULL, 4, 'module-ipv6', 5, 240,
 'security', ARRAY['klausur-advanced', 'klausur-security']),

('cued',
 'Warum ist bei IPv6 Port Scanning auf Netzebene praktisch wirkungslos?',
 'Ein /64-Subnetz hat 2^64 ≈ 1,8 × 10^19 mögliche Host-Adressen. Auch bei 1 Million Scans pro Sekunde bräuchte man ~580 Tausend Jahre um das Subnetz komplett zu scannen.\n\nIm Vergleich IPv4 /24: 256 Adressen, in <1 Sekunde durchgeprüft.\n\nFolge:\n- Angreifer können nicht mehr blind nach Hosts suchen — sie brauchen DNS-Einträge, Logs, geleakte Adressen.\n- Wichtig: Privacy Extensions aktivieren, damit Adressen nicht durch EUI-64 vorhersehbar werden.\n- Aber: Zuverlässige Schutzwirkung nur wenn keine vorhersehbaren Muster verwendet werden (z.B. ::1, ::2, ::dead:beef).\n\nKlausur-Antwort: „Adress-Raum eines /64 so groß dass sequentielles Scannen unmöglich ist — Security by Address-Space".',
 '{"required_concepts": ["2^64", "sequenziell unmöglich", "Privacy Extensions", "keine vorhersehbaren Muster"]}',
 NULL, 3, 'module-ipv6', 4, 150,
 'security', ARRAY['klausur-advanced']),

-- ============================================================
-- SUB-AREA: troubleshoot (3 items)
-- ============================================================

('cued',
 'Welche Kommandozeilen-Tools prüfen IPv6-Konnektivität auf Windows und Linux?',
 'Windows:\n- ipconfig /all — zeigt alle IPv6-Adressen (auch Link-Local) + Default-Gateway + DNS\n- ping ::1 bzw. ping -6 <adresse> — Loopback / Connectivity-Test\n- tracert -6 <adresse> — Traceroute IPv6\n- netsh interface ipv6 show addresses — detailliert\n- netsh interface ipv6 show neighbors — Neighbor Cache (ARP-Ersatz)\n\nLinux:\n- ip -6 addr show — alle IPv6-Adressen\n- ip -6 route show — Routing-Tabelle\n- ip -6 neigh show — Neighbor Cache\n- ping6 / ping -6 — Connectivity\n- traceroute6 / tracepath6\n- ss -6tulpn — welche Sockets lauschen auf IPv6',
 '{"required_concepts": ["ipconfig /all", "ping6 / ping -6", "ip -6 addr", "ip -6 neigh", "tracert -6"]}',
 NULL, 3, 'module-ipv6', 2, 120,
 'troubleshoot', ARRAY['klausur-standard', 'operator-nennen']),

('cued',
 'Ein IPv6-Client bekommt via SLAAC eine Adresse, aber hat keinen Internet-Zugang. Was prüfst du in welcher Reihenfolge?',
 'OSI-Bottom-Up:\n\n1. Link (Layer 2): Kabel / WLAN ok? `ip link show` zeigt Interface UP?\n2. Link-Local: `ip -6 addr` — fe80::/10 Adresse vorhanden? (wenn nein, IPv6-Stack nicht aktiv)\n3. Router gefunden? `ip -6 route` — Default Route über fe80 des Routers?\n4. Globale Adresse: Präfix korrekt vergeben? `ip -6 addr` zeigt 2xxx::/64?\n5. Router erreichbar? `ping6 <Link-Local-Router>` (mit Interface-Scope: `ping6 fe80::1%eth0`)\n6. DNS ok? `nslookup google.com` liefert AAAA-Record? (wenn nein, DNS-Server nicht gesetzt oder falsch)\n7. Externe Adresse: `ping6 2001:4860:4860::8888` (Google DNS) — antwortet?\n8. MTU-Problem? `ping6 -M do -s 1400 2001:4860:4860::8888` — PMTUD ok?\n9. Firewall blockt ICMPv6/NDP? In RA-Guard-Logs / `iptables -L` checken.',
 '{"required_concepts": ["OSI Bottom-Up", "fe80 Link-Local", "ip -6 route", "Ping fe80::1%eth0", "PMTUD", "DNS AAAA"]}',
 NULL, 5, 'module-ipv6', 5, 360,
 'troubleshoot', ARRAY['klausur-advanced', 'operator-beschreiben']),

('cued',
 'Wie erkennst du dass Privacy Extensions aktiv sind?',
 'Windows:\n`netsh interface ipv6 show privacy` — Zeigt "Privacy enabled: enabled/disabled"\n\nOder `ipconfig /all` — bei aktiven Privacy Extensions sieht man:\n- "IPv6-Adresse. . . : 2001:db8::abcd (Preferred)" — die zufällige (temp) Adresse\n- "Temporäre IPv6-Adresse: 2001:db8::xyz (Preferred)"  — alternativ\n- "Verbindungslokale IPv6-Adresse: fe80::... (Preferred)"\n\nLinux:\n`cat /proc/sys/net/ipv6/conf/<iface>/use_tempaddr`\n- 0 = aus\n- 1 = Privacy-Adresse bevorzugt für ausgehend (default modern)\n- 2 = Privacy-Adresse erzwungen\n\n`ip -6 addr` zeigt bei aktiven PE zwei globale Adressen — eine EUI-64, eine mit „temporary" Flag.',
 '{"required_concepts": ["netsh show privacy", "use_tempaddr", "zwei globale Adressen", "temporary Flag"]}',
 NULL, 3, 'module-ipv6', 4, 150,
 'troubleshoot', ARRAY['klausur-advanced'])

) AS v(
    item_type, prompt, model_answer, expected_answer_structure,
    grading_criteria, points, source_exam, difficulty, estimated_time_sec,
    sub_area, tags
);

-- ============================================================================
-- Teil 4: Neue Items dem IPv6-Modul zuordnen (use_in='mastery', pool_tier=1)
-- ============================================================================

INSERT INTO assessments.ap2_module_items (module_id, item_id, pool_tier, use_in, sort_order)
SELECT
    (SELECT module_id FROM assessments.ap2_modules WHERE slug = 'ipv6-konfiguration'),
    i.item_id,
    1,
    'mastery',
    100 + ROW_NUMBER() OVER (ORDER BY i.created_at)
FROM assessments.ap2_learning_items i
WHERE i.source_exam = 'module-ipv6'
  AND i.sub_area IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM assessments.ap2_module_items mi
     WHERE mi.item_id = i.item_id
  );

-- Unique Constraint auf Item-ID im Modul-Pool (falls noch nicht vorhanden)
-- (Repeat-Safety: das Unique-Index existiert in der bestehenden Migration schon)

COMMIT;
