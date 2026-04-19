-- ============================================================================
-- Migration: 129_ap2_osi_deep.sql
-- Description: OSI-Schlüsselthema auf Lindner-Dozenten-Niveau ausbauen.
--              Basiert auf "OSI am Bsp.pdf" (LAMPP-Web-Aufruf) + AP1-2026-BW.
--              Deckt ab:
--              — Kompletter Web-Aufruf L7→L1 (Client) → Netzwerk → L1→L7 (Server)
--              — PDU-Namen (Bits/Frame/Paket/Segment/Daten)
--              — ARP-Mechanismus (Broadcast-Anfrage, L2)
--              — Tools pro Schicht (ping/traceroute/netstat/nslookup/tcpdump...)
--              — Encapsulation / Decapsulation
--              — Switch-vs-Router-Layer-Unterscheidung
--              — E-Mail-Versand (SMTP/IMAP) OSI-Mapping
--              — Fehlersuche systematisch L1 bis L7
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
-- OSI — Kompletter Web-Aufruf-Walkthrough (BW-Klassiker)
-- ============================================================

('osi-troubleshooting', 'blurt',
 'Ein Mitarbeiter der Firma „Agrarenergie Müller e. K." ruft im Browser die URL http://192.168.0.10/index.php auf. Der Server ist ein Apache/PHP/MySQL-System im gleichen Subnetz. Beschreibe Schicht für Schicht, was auf dem Client passiert (L7→L1), was das Netzwerk macht, und was auf dem Server in der Decapsulation passiert (L1→L7). Nenne pro Schicht: was konkret passiert, welches Protokoll/Bauteil beteiligt ist und welche PDU (Protocol Data Unit) entsteht.',
 'CLIENT — Encapsulation L7 → L1:
L7 Anwendung: Browser baut HTTP-GET: "GET /index.php HTTP/1.1", Host-Header, User-Agent. PDU: Daten.
L6 Darstellung: Zeichensatz UTF-8, ggf. gzip-Kompression, bei HTTPS TLS-Verschlüsselung + Zertifikat.
L5 Sitzung: TCP-Session aufbauen oder bestehende verwenden, Cookies + Session-ID verwalten, Keep-Alive.
L4 Transport: TCP, Quellport z.B. 49532, Zielport 80. 3-Way-Handshake (SYN → SYN-ACK → ACK). Segmentierung + Reihenfolge via Sequenznummern. PDU: Segment.
L3 Vermittlung: IP-Header: Quell-IP 192.168.0.20, Ziel-IP 192.168.0.10, Protokollfeld TCP (6). Gleiches Subnetz → direkter Versand, sonst Standard-Gateway. PDU: Paket.
L2 Sicherung: ARP-Broadcast: "Wer hat 192.168.0.10?" → Antwort mit MAC. Ethernet-Frame mit Quell-MAC + Ziel-MAC + EtherType 0x0800 (IPv4) + FCS-Prüfsumme. PDU: Frame.
L1 Bitübertragung: Frame wird als elektrische Signale über UTP-Kabel gesendet. PDU: Bits.

NETZWERK:
Switch (L2): liest Ziel-MAC, schaut in MAC-Adresstabelle, leitet Frame an passenden Port.
Router (L3, falls anderes Subnetz): wertet Ziel-IP aus, routet anhand Routing-Tabelle.

SERVER — Decapsulation L1 → L7:
L1: NIC empfängt Bits.
L2: prüft FCS, prüft "Ziel-MAC = meine MAC?", entfernt Frame-Header.
L3: prüft "Ziel-IP = meine IP?", entfernt IP-Header.
L4 TCP: sieht Port 80 → reicht Payload an Apache-Prozess. Sendet ACK zurück.
L5/L6: TLS-Handshake abschließen (bei HTTPS), Session verwalten.
L7: Apache ruft mod_php auf, PHP führt index.php aus, MySQL-Query via PDO, PHP generiert HTML-Response.

Antwort: Gleicher Weg rückwärts, aber IPs + Ports getauscht (Server → Client).',
 '{"required_concepts": ["L7 HTTP GET Header", "L6 UTF-8 TLS Zertifikat", "L5 Session Keep-Alive Cookie", "L4 TCP Port 3-Way-Handshake", "L3 IP Subnetz Gateway", "L2 ARP Broadcast Ethernet Frame FCS", "L1 Kabel Bits", "PDU Bits Frame Paket Segment Daten", "Switch L2 MAC-Tabelle", "Router L3 Routing-Tabelle", "Server Decapsulation L1 bis L7", "Apache mod_php MySQL"]}',
 '[{"criterion": "Alle 7 Schichten Client-Richtung", "weight": 5, "description": "L7 bis L1 mit Inhalt", "required": true},
   {"criterion": "PDU-Namen korrekt", "weight": 3, "description": "Bits/Frame/Paket/Segment/Daten", "required": true},
   {"criterion": "3-Way-Handshake erwähnt", "weight": 2, "description": "SYN/SYN-ACK/ACK", "required": true},
   {"criterion": "ARP-Mechanismus", "weight": 2, "description": "Broadcast für MAC-Auflösung", "required": true},
   {"criterion": "Switch-L2 / Router-L3 unterschieden", "weight": 2, "description": "MAC vs IP", "required": true},
   {"criterion": "Server-Decapsulation vollständig", "weight": 4, "description": "L1 bis L7 rückwärts", "required": true},
   {"criterion": "Apache-PHP-MySQL-Kette", "weight": 2, "description": "L7 konkretisiert", "required": false}]',
 20, 'W2026-BW-Lindner-OSI-Walkthrough', 5, 1500),

-- ============================================================
-- OSI — PDU / Layer-Zuordnung (Kurzfragen)
-- ============================================================

('osi-troubleshooting', 'cued',
 'Welche Protocol Data Unit (PDU) gehört zu welcher OSI-Schicht?',
 'L1 Bitübertragung: Bits.\nL2 Sicherung: Frame.\nL3 Vermittlung: Paket.\nL4 Transport: Segment (bei TCP) / Datagramm (bei UDP).\nL5-L7 Sitzung/Darstellung/Anwendung: Daten (engl. Data / PDU).\n\nEselsbrücke: "Bitte Frage Paul Sein Daten" — Bits / Frame / Paket / Segment / Daten.',
 '{"required_concepts": ["L1 Bits", "L2 Frame", "L3 Paket", "L4 Segment Datagramm", "L5-7 Daten"]}',
 NULL, 5, 'ki-generated-lindner', 3, 240),

('osi-troubleshooting', 'cued',
 'Ordnen Sie jedes Protokoll der korrekten OSI-Schicht zu: HTTP, TCP, IP, Ethernet, ARP, TLS, DNS, ICMP, UDP, MAC, FTP, DHCP.',
 'L7 Anwendung: HTTP, FTP, DNS, DHCP (nutzt UDP, ist aber Anwendungsprotokoll).\nL6 Darstellung: TLS/SSL (Übergang L5/L6, IHK-Konvention: L6).\nL5 Sitzung: — (oft keine expliziten Protokolle in IHK-Klausuren).\nL4 Transport: TCP, UDP.\nL3 Vermittlung: IP (v4/v6), ICMP, ARP (technisch L2/L3-Grenze, in IHK-BW meist als L2 zugeordnet).\nL2 Sicherung: Ethernet, MAC, ARP.\nL1 Bitübertragung: Kabel, Stecker, Lichtimpulse.\n\nMerkhilfe für IHK: "HFDD (L7) TLS (L6) TCP-UDP (L4) IP-ICMP (L3) Ethernet-MAC-ARP (L2)".',
 '{"required_concepts": ["HTTP L7", "TLS L6", "TCP L4", "IP L3", "Ethernet L2", "ARP L2-L3-Grenze", "UDP L4", "ICMP L3", "DNS L7 nutzt UDP", "MAC L2"]}',
 NULL, 8, 'ki-generated-lindner', 4, 360),

('osi-troubleshooting', 'cued',
 'Auf welcher OSI-Schicht arbeiten folgende Netzwerkgeräte: Hub, Switch, Router, Firewall, Load Balancer, Proxy-Server, WLAN Access Point?',
 'Hub: L1 (Bitübertragung) — leitet einfach Signale weiter, ohne sie zu verstehen. Macht Kollisionen.\nSwitch: L2 (Sicherung) — kennt MAC-Adressen, leitet zielgerichtet weiter. Moderne Switches auch L3 (Layer-3-Switch).\nRouter: L3 (Vermittlung) — routet anhand IP-Adressen zwischen Subnetzen.\nFirewall: meist L3/L4 (stateful: prüft IP + Port); Next-Generation-Firewalls bis L7 (Deep Packet Inspection).\nLoad Balancer: L4 (Port-basiert) oder L7 (Applikations-aware).\nProxy-Server: L7 (HTTP/HTTPS verstehen, Inhalt cachen/filtern).\nWLAN AP: L1 + L2 (Funk = L1, MAC-Adressierung + CSMA/CA = L2).\n\nRegel: Je höher die Schicht, desto mehr Inhaltsverständnis — aber auch langsamer.',
 '{"required_concepts": ["Hub L1", "Switch L2 optional L3", "Router L3", "Firewall L3-L4 Next-Gen L7", "Load Balancer L4 oder L7", "Proxy L7", "WLAN AP L1-L2"]}',
 NULL, 7, 'ki-generated-lindner', 4, 360),

-- ============================================================
-- OSI — ARP-Mechanismus (häufige Prüfungsfrage)
-- ============================================================

('osi-troubleshooting', 'cued',
 'Erklären Sie den ARP-Mechanismus: Wann kommt er zum Einsatz, was ist die Anfrage, was ist die Antwort, auf welcher OSI-Schicht läuft er ab? Wie sieht der ARP-Cache aus?',
 'Einsatz: Wenn ein Host einem anderen Host im gleichen Subnetz ein IP-Paket schicken will, kennt er dessen IP, aber noch nicht die MAC. Da Ethernet-Frames (L2) MAC-Adressen brauchen, muss er die MAC zur IP auflösen.\n\nAnfrage (Broadcast auf L2):\nAbsender: eigene MAC/IP.\nZiel-MAC: FF:FF:FF:FF:FF:FF (Broadcast).\nFrage: "Wer hat IP 192.168.0.10? Bitte an MAC aa:bb:cc:dd:ee:ff antworten."\n\nAntwort (Unicast auf L2):\nDer Host mit 192.168.0.10 antwortet direkt: "192.168.0.10 ist bei MAC 11:22:33:44:55:66."\n\nSchicht: ARP sitzt technisch zwischen L2 und L3 (löst L3-Adresse → L2-Adresse). In IHK-BW meist als L2 gewertet, aber IT-Klausuren schreiben oft "Grenze L2/L3".\n\nARP-Cache anzeigen:\n- Linux: `ip neigh` oder `arp -n`\n- Windows: `arp -a`\n\nBeispielausgabe:\n  192.168.0.1    00:1A:2B:3C:4D:5E   ether (Gateway)\n  192.168.0.10   11:22:33:44:55:66   ether (Server)',
 '{"required_concepts": ["IP zu MAC Auflösung", "gleiche Subnetz", "Broadcast FF:FF:FF:FF:FF:FF", "Unicast-Antwort", "L2 oder L2/L3-Grenze", "arp -a Windows", "ip neigh Linux"]}',
 NULL, 6, 'ki-generated-lindner', 4, 360),

-- ============================================================
-- OSI — Fehlersuche-Aufgabe (BW-Stil Projekt-Szenario)
-- ============================================================

('osi-troubleshooting', 'application',
 'Ein Mitarbeiter der „Schnellinger GmbH" meldet: „Ich kann das interne Intranet-Portal https://intranet.schnellinger.local nicht mehr erreichen — es kommt keine Verbindung zustande." Beschreiben Sie systematisch eine Fehlersuche von Schicht 1 bis Schicht 7. Nennen Sie pro Schicht mindestens ein konkretes Tool/Kommando und eine Prüffrage.',
 'L1 Bitübertragung:
Tool: LED-Status am Switch-Port, Kabeltester, `ethtool eth0`.
Prüffrage: Ist das Netzwerkkabel gesteckt? Leuchtet die Link-LED? Ist das Kabel intakt?

L2 Sicherung:
Tool: `arp -a` / `ip neigh`, Switch-MAC-Tabelle.
Prüffrage: Sehe ich die MAC des Gateways im ARP-Cache? Bin ich im richtigen VLAN (falls VLANs)?

L3 Vermittlung:
Tool: `ipconfig` / `ip addr`, `ping <Gateway>`, `ping <DNS-Server>`, `ping 8.8.8.8`, `traceroute intranet.schnellinger.local`.
Prüffrage: Habe ich eine IP-Adresse? Kann ich das Gateway erreichen? Läuft das Routing zum Intranet-Server?

L4 Transport:
Tool: `telnet intranet.schnellinger.local 443`, `nc -vz intranet... 443`, `netstat -tln` (am Server).
Prüffrage: Ist Port 443 offen? Blockiert die Firewall TCP/443?

L5/L6:
Tool: Browser-Devtools, `openssl s_client -connect intranet.schnellinger.local:443`.
Prüffrage: Ist das TLS-Zertifikat gültig? Nicht abgelaufen? Korrekte Zertifikatskette?

L7 Anwendung:
Tool: `nslookup intranet.schnellinger.local`, `dig intranet...`, `curl -v https://intranet.schnellinger.local`, Browser-Cache leeren.
Prüffrage: Löst DNS den Namen korrekt auf? Antwortet der Webserver mit 200 OK? Ist im Apache/nginx-Log ein Fehler?

Systematik: Immer von unten nach oben testen. Wenn L3-Ping erfolgreich aber L4-telnet fehlschlägt → Firewall oder Dienst-Problem. Wenn Browser-Fehler aber curl ok → Browser-Cache/Cookies.',
 '{"required_concepts": ["L1 LED Kabeltester", "L2 arp Cache VLAN", "L3 ping traceroute ipconfig", "L4 telnet Port netstat", "L5/6 TLS openssl", "L7 nslookup curl Logs", "systematisch unten nach oben"]}',
 '[{"criterion": "Alle 7 Schichten abgedeckt", "weight": 4, "description": "jede Schicht ein Tool", "required": true},
   {"criterion": "Tools korrekt", "weight": 4, "description": "passend zur Schicht", "required": true},
   {"criterion": "Prüffrage pro Schicht", "weight": 3, "description": "sinnvoll formuliert", "required": true},
   {"criterion": "Systematik beschrieben", "weight": 1, "description": "unten nach oben", "required": false}]',
 12, 'W2026-BW-Schnellinger-Fehlersuche', 5, 1500),

-- ============================================================
-- OSI — E-Mail-Versand (Email_OSI.docx Dozentenmaterial)
-- ============================================================

('osi-troubleshooting', 'application',
 'Ein Mitarbeiter schreibt in Outlook eine E-Mail an extern@example.com und klickt „Senden". Beschreiben Sie den Weg der E-Mail durch das OSI-Modell vom Outlook-Client bis zum Empfänger-Postfach. Welche Protokolle kommen in welcher Schicht zum Einsatz? Welche Transportwege gibt es beim Abrufen der Antwort?',
 'VERSAND (Outlook → externer Mailserver):
L7 Anwendung: SMTP (Simple Mail Transfer Protocol), Port 25 / 587 (Submission) / 465 (SMTPS).
L6 Darstellung: MIME (Multipurpose Internet Mail Extensions) encodiert Anhänge als Base64; TLS/STARTTLS verschlüsselt Session.
L5 Sitzung: SMTP-Session mit EHLO/MAIL FROM/RCPT TO/DATA/QUIT; Auth via AUTH LOGIN oder SASL.
L4 Transport: TCP Port 587 (Submission) oder 465 (SMTPS). Reliable, in-order.
L3 Vermittlung: IP-Routing zum Mailserver (ggf. über Internet).
L2 Sicherung: Ethernet-Frames mit MAC (vom Client → Router → Provider → Ziel-MTA).
L1 Bitübertragung: physische Signale über Kupfer/LWL/Funk.

Route: Outlook → eigener SMTP-Server (z.B. mail.schnellinger.local:587) → MX-Lookup für example.com (DNS Query!) → Ziel-MTA (z.B. mx.example.com:25) → Postfach des Empfängers.

ABRUFEN der Antwort (Empfänger → eigener Mailserver → Outlook):
L7: POP3 (Port 110/995-SSL, lädt runter und löscht meist) ODER IMAP (Port 143/993-SSL, synchronisiert, lässt auf Server). Moderne Clients nutzen IMAP.
L6: MIME-Decoding, TLS.
L5-L1 identisch wie oben.

Zusätzliche Protokolle: SPF/DKIM/DMARC (Anti-Spam, auf L7), MX-Record-Lookup via DNS (L7, UDP/TCP Port 53).',
 '{"required_concepts": ["SMTP L7", "MIME L6 Base64", "TLS/STARTTLS L6", "TCP 25/587/465 L4", "POP3 L7 runterladen", "IMAP L7 synchronisieren", "993/995 SSL-Varianten", "MX-Record DNS-Lookup", "SPF DKIM DMARC"]}',
 '[{"criterion": "SMTP für Versand", "weight": 2, "description": "L7 + Port 25/587", "required": true},
   {"criterion": "POP3 vs IMAP erklärt", "weight": 3, "description": "Unterschied Sync vs Download", "required": true},
   {"criterion": "MIME/Base64 für Anhänge", "weight": 2, "description": "L6 Darstellung", "required": true},
   {"criterion": "TLS/STARTTLS-Varianten", "weight": 2, "description": "Verschlüsselung", "required": true},
   {"criterion": "MX-Record/DNS-Lookup", "weight": 2, "description": "L7 vor Versand", "required": true},
   {"criterion": "Ports korrekt", "weight": 2, "description": "25/587/465/110/995/143/993", "required": false}]',
 12, 'W2026-BW-Email-OSI', 5, 1500),

-- ============================================================
-- OSI — Switch vs. Router (klassische BW-Unterscheidungsfrage)
-- ============================================================

('osi-troubleshooting', 'cued',
 'Vergleichen Sie Switch und Router hinsichtlich: OSI-Schicht, Adressierungsart, Weiterleitungsentscheidung, Broadcast-Domain, typische Platzierung im Netzwerk.',
 'Switch:\n- OSI-Schicht: L2 (Sicherung). Moderne Layer-3-Switches können auch L3.\n- Adressierung: MAC-Adressen (physisch, 48 Bit).\n- Entscheidung: MAC-Adresstabelle (selbstlernend über Absender-MAC eingehender Frames).\n- Broadcast-Domain: Alle Ports = eine Broadcast-Domain (außer VLAN-Trennung).\n- Platzierung: Innerhalb eines Subnetzes/VLANs, meist als Access-Switch am Arbeitsplatz oder Core-Switch im Serverraum.\n\nRouter:\n- OSI-Schicht: L3 (Vermittlung).\n- Adressierung: IP-Adressen (logisch, 32 Bit IPv4 / 128 Bit IPv6).\n- Entscheidung: Routing-Tabelle (statisch konfiguriert oder dynamisch via OSPF/BGP gelernt).\n- Broadcast-Domain: Trennt Broadcast-Domains — Broadcasts werden nicht weitergeleitet.\n- Platzierung: An der Grenze zwischen Subnetzen, zum Internet (Edge-Router), zwischen Standorten (Site-to-Site).\n\nMerkregel: "Switch spricht MAC, Router spricht IP. Switch bleibt im Netz, Router verbindet Netze."',
 '{"required_concepts": ["Switch L2 MAC", "Router L3 IP", "MAC-Tabelle vs Routing-Tabelle", "Switch eine Broadcast-Domain", "Router trennt Broadcast-Domains", "VLAN-Trennung erwähnt", "Edge-Router Site-to-Site"]}',
 NULL, 6, 'ki-generated-lindner', 3, 360),

-- ============================================================
-- OSI — 3-Way-Handshake (Details)
-- ============================================================

('osi-troubleshooting', 'cued',
 'Beschreiben Sie den TCP-3-Way-Handshake in seinen drei Schritten. Welche Flags werden gesetzt, welche Sequenznummern ausgetauscht? Auf welcher OSI-Schicht läuft der Handshake ab?',
 '3-Way-Handshake (TCP-Verbindungsaufbau, L4 Transport):

Schritt 1 — SYN:\nClient → Server: TCP-Segment mit Flag SYN=1, Sequenznummer x (zufällig gewählt).\nBedeutung: "Ich möchte eine Verbindung aufbauen, meine Startnummer ist x."

Schritt 2 — SYN-ACK:\nServer → Client: TCP-Segment mit Flags SYN=1, ACK=1. Sequenznummer y (zufällig). ACK-Nummer = x+1.\nBedeutung: "Ich akzeptiere. Meine Startnummer ist y. Ich bestätige deine x (erwarte jetzt x+1)."

Schritt 3 — ACK:\nClient → Server: TCP-Segment mit Flag ACK=1. Sequenznummer x+1, ACK-Nummer y+1.\nBedeutung: "Bestätigt. Ab jetzt nutzen wir die Sequenzen für den Datenaustausch."

Ab jetzt können Payload-Daten fließen.\n\nVerbindungsabbau braucht 4-Way-Handshake (FIN → ACK → FIN → ACK), weil beide Richtungen einzeln geschlossen werden müssen.\n\nSchicht: L4 Transport.',
 '{"required_concepts": ["SYN", "SYN-ACK", "ACK", "Sequenznummer x y", "x+1 Bestätigung", "L4 Transport", "4-Way Verbindungsabbau FIN"]}',
 NULL, 5, 'ki-generated-lindner', 4, 360),

-- ============================================================
-- OSI — Schicht 5/6 (oft unterschätzt in BW)
-- ============================================================

('osi-troubleshooting', 'cued',
 'Schicht 5 (Sitzung) und Schicht 6 (Darstellung) werden oft vergessen. Nennen Sie konkrete Protokolle/Aufgaben pro Schicht — auch wenn sie in der Praxis häufig in L7 integriert sind.',
 'L5 Sitzung (Session):\n- Aufbau, Verwaltung und Abbau von Sitzungen zwischen Anwendungen.\n- Checkpoints bei langen Übertragungen (z.B. Datei-Transfer), Wiederaufnahme nach Unterbrechung.\n- Protokolle: NetBIOS-Session-Service, RPC (Remote Procedure Call), SMB-Sessions, PPTP.\n- In modernen TCP/IP-Stacks meist in L7 integriert (HTTP-Session via Cookie, TLS-Session-Resumption).\n\nL6 Darstellung (Presentation):\n- Daten-Repräsentation plattformübergreifend: Zeichensätze (ASCII/UTF-8/UTF-16), Endianness (Big/Little).\n- Kompression (gzip, deflate).\n- Verschlüsselung + Authentizität: TLS/SSL, S/MIME für E-Mail.\n- Serialisierungsformate: JSON, XML, ASN.1, MIME, Base64.\n\nMerkregel für IHK: "L5 = Wie lange bleiben wir verbunden? L6 = Wie sieht die Nachricht konkret aus?"',
 '{"required_concepts": ["L5 Session Aufbau Abbau Checkpoint", "RPC NetBIOS SMB", "L6 Darstellung Zeichensatz UTF-8", "TLS S/MIME", "Kompression gzip", "Serialisierung JSON XML Base64", "HTTP-Session Cookie"]}',
 NULL, 5, 'ki-generated-lindner', 4, 300),

-- ============================================================
-- OSI — Encapsulation/Decapsulation Begriff
-- ============================================================

('osi-troubleshooting', 'cued',
 'Was bedeuten die Begriffe Encapsulation und Decapsulation im OSI-Modell? Zeichnen Sie (als Text-Skizze) das „Zwiebelschalen-Prinzip" einer fertigen Ethernet-Übertragung.',
 'Encapsulation (Einpacken, am Sender, L7→L1):\nJede Schicht fügt ihren eigenen Header (manchmal auch Trailer) an die Payload der darüberliegenden Schicht. Die gesamte PDU der höheren Schicht wird so zur Payload der tieferen Schicht.\n\nDecapsulation (Auspacken, am Empfänger, L1→L7):\nUmgekehrter Vorgang — jede Schicht entfernt ihren Header, prüft ihn, reicht die Payload an die nächsthöhere Schicht.\n\nZwiebelschalen-Skizze eines Ethernet-Frames, der einen HTTP-GET überträgt:\n\n[Ethernet-Header | [IP-Header | [TCP-Header | [HTTP-Daten: GET /index.php HTTP/1.1 Host:... ] ] ] | Ethernet-Trailer (FCS)]\n  L2                 L3             L4              L7                                          L2\n\nJede Schicht sieht nur ihre Payload als "opake" Nutzlast und kümmert sich nicht um den Inhalt.\n\nKonsequenz: Paketgrößen summieren sich. MTU (Maximum Transmission Unit) bei Ethernet = 1500 Byte. Davon z.B. 20 Byte IP-Header + 20 Byte TCP-Header = nur 1460 Byte für HTTP-Daten pro Segment.',
 '{"required_concepts": ["Encapsulation L7 zu L1 Header anfügen", "Decapsulation L1 zu L7", "Zwiebelschalen-Skizze", "Payload der höheren Schicht wird Payload der tieferen", "MTU 1500 Ethernet", "Header-Overhead TCP 20 IP 20"]}',
 NULL, 5, 'ki-generated-lindner', 4, 360),

-- ============================================================
-- OSI — Diagnose-Tools-Zuordnung
-- ============================================================

('osi-troubleshooting', 'cued',
 'Ordnen Sie folgende Diagnose-Tools der passenden OSI-Schicht zu und beschreiben Sie deren Zweck: ping, traceroute, arp -a, ipconfig, nslookup, telnet, nmap, tcpdump, openssl s_client, curl, ethtool.',
 'L1 (Bitübertragung):\n- `ethtool eth0` — Linkstatus, Geschwindigkeit, Duplex.\n\nL2 (Sicherung):\n- `arp -a` / `ip neigh` — ARP-Cache anzeigen (MAC zu IP).\n\nL3 (Vermittlung):\n- `ipconfig` (Windows) / `ip addr` (Linux) — eigene IP-Konfiguration.\n- `ping <host>` — IP-Erreichbarkeit + Laufzeit (ICMP).\n- `traceroute` / `tracert` — Route zum Ziel (ICMP/UDP).\n\nL4 (Transport):\n- `telnet <host> <port>` — Port-Erreichbarkeit prüfen.\n- `nmap -p 80,443 <host>` — Port-Scan.\n- `netstat -tln` / `ss -tln` — offene Ports lokal.\n\nL4-L7 (Protokoll-Analyse):\n- `tcpdump -i eth0 port 80` — Paket-Mitschnitt auf der Kommandozeile.\n- Wireshark — grafischer Paket-Analyzer.\n\nL6 (Darstellung — TLS):\n- `openssl s_client -connect host:443` — TLS-Handshake + Zertifikat prüfen.\n\nL7 (Anwendung):\n- `nslookup hostname` / `dig hostname` — DNS-Auflösung.\n- `curl -v https://...` — HTTP-Request mit Verbose-Output.\n- Browser-Devtools — Request/Response-Analyse.\n\nMerkhilfe: Je höher das Tool, desto mehr sagt es über den Anwendungsinhalt aus.',
 '{"required_concepts": ["ethtool L1", "arp L2", "ipconfig ping L3", "traceroute L3", "telnet nmap L4", "netstat L4", "tcpdump L4-7", "openssl L6", "nslookup curl L7"]}',
 NULL, 8, 'ki-generated-lindner', 4, 480)

) AS v(slug, item_type, prompt, model_answer,
       expected_answer_structure, grading_criteria, points, source_exam, difficulty, estimated_time_sec)
JOIN topic_lookup t ON t.slug = v.slug;

-- OSI ist klassischer BW-Prüfungsschwerpunkt — sehr-hoch, 20 Punkte erwartet
UPDATE assessments.ap2_topics
SET expected_points = 20,
    priority = 'sehr-hoch'
WHERE slug = 'osi-troubleshooting';

COMMIT;
