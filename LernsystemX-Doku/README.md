# LernsystemX Dokumentation

> **40 Dokumente** in **7 Kategorien** - Vollständige Systemdokumentation

---

## Schnellnavigation

| Kategorie | Beschreibung | Docs |
|-----------|--------------|------|
| [01_Core](#01_core---kernsystem) | System-Grundlagen, Rollen, Lernmethoden | 7 |
| [02_Business](#02_business---geschäftsmodelle) | Premium, Creator, Pricing, Organisationen | 5 |
| [03_Features](#03_features---feature-systeme) | Community, Dashboard, Editor, LiveRoom | 7 |
| [04_KI](#04_ki---ki-systeme) | KI-Pipeline, Authoring-Studio, Agents | 5 |
| [05_Technical](#05_technical---technische-architektur) | DB, API, Frontend, Backend | 7 |
| [06_DevOps](#06_devops---betrieb--infrastruktur) | Security, Deployment, Monitoring | 6 |
| [07_Setup-Dev](#07_setup-dev---setup--entwicklung) | Installation, Admin, Developer-Guide | 3 |

---

## 01_Core - Kernsystem

Grundlegende Systemkonzepte und Architektur.

| Datei | Beschreibung |
|-------|--------------|
| `00_System-Übersicht` | Gesamtübersicht, C4-Diagramme, Architektur |
| `01_Rollenmodell` | 9 Benutzerrollen (Free → Admin) mit Berechtigungen |
| `02_Lernmethoden` | **Master-Dokument:** 12 Content-Lernmethoden (Gruppen A-C) |
| `02a_System-Features` | System-Features (frühere LMs D-F): Tutor, IT-Sandbox, Kollaboration |
| `03_Zugriffssystem` | Berechtigungen, Zugriffskontrolle, RBAC |
| `04_Kurs-Architektur` | Kurs → Kapitel → Lektionen → Lernmethoden |
| `05_Sicherheit-Berechtigungen` | Authentifizierung, Autorisierung, JWT |

---

## 02_Business - Geschäftsmodelle

Monetarisierung und Organisationsstrukturen.

| Datei | Beschreibung |
|-------|--------------|
| `01_Premium-Modell` | Premium-Abo (14,99€/Monat), Token-System, Features |
| `02_Creator-Modell` | Content-Ersteller, 75% Revenue Share, Marketplace |
| `03_Price-Engine` | Dynamische Preisberechnung, Rabatte, Bundles |
| `04_Schulen-Unternehmen` | Enterprise-Features, Klassen, Mitarbeiterverwaltung |
| `05_Organisation-System` | Multi-Org, Token-Pools, Branding, Domains |

---

## 03_Features - Feature-Systeme

Benutzer-Features und Interaktionssysteme.

| Datei | Beschreibung |
|-------|--------------|
| `01_Community-System` | Gruppen, Foren, Kurs-Sharing, Social Features |
| `02_Dashboard-System` | Personalisierbare Dashboards, Widgets |
| `03_Widget-System` | 15+ Widget-Typen, Konfiguration, Registry |
| `04_Editor-System` | Kurs-Editor, Methoden-Editoren, KI-Unterstützung |
| `05_LiveRoom-System` | WebRTC, Video/Audio, Whiteboard, Aufzeichnung |
| `06_Internationalisierung` | i18n-Framework, Locale-Management |
| `07_Übersetzungs-System` | DeepL-Integration, 20 Sprachen, Auto-Übersetzung |

---

## 04_KI - KI-Systeme

Künstliche Intelligenz und Automatisierung.

| Datei | Beschreibung |
|-------|--------------|
| `01_KI-Pipeline` | 13 KI-Module: Import, Generierung, Validierung |
| `01a_KI-Pipeline-Implementierung` | Technische Details: Worker, Queue, Cache, Prompts |
| `02_KI-Authoring-Studio` | Desktop-Tool für KI-gestützte Kurserstellung |
| `03_Smart-Agent-System` | Wissens-Caching, Token-Ersparnis (50-70%) |
| `04_3D-Avatar-Feedback` | VRM-Avatare, Lip-Sync, Tutor-Visualisierung |

---

## 05_Technical - Technische Architektur

Datenbank, APIs und Code-Struktur.

| Datei | Beschreibung |
|-------|--------------|
| `01_DB-Struktur` | PostgreSQL-Schema, 114+ Tabellen, Migrationen |
| `02_API-Spezifikation` | REST-API-Dokumentation, Endpunkte, Responses |
| `03_API-Gateway` | Routing, Rate-Limiting, Versionierung |
| `04_Frontend-Struktur` | Vue.js 3, Pinia, Komponenten-Architektur |
| `05_Backend-Struktur` | Flask, Repository-Pattern, Services |
| `06_Kurs-Kategorisierung` | Flexibles Kategorie-System, unbegrenzte Tiefe |
| `07_Analytics-System` | Metriken, Dashboards, Datenquellen |

---

## 06_DevOps - Betrieb & Infrastruktur

Deployment, Sicherheit und Monitoring.

| Datei | Beschreibung |
|-------|--------------|
| `01_Security-Architecture` | Security-Konzept, Verschlüsselung, Auditing |
| `02_Caching-Strategy` | Redis, Cache-Invalidierung, Performance |
| `03_Deployment-DevOps` | Docker, Nginx, Systemd, CI/CD |
| `04_Backup-Recovery` | Backup-Strategien, Restore, Disaster Recovery |
| `05_Monitoring-Alerting` | Prometheus, Grafana, Alerting-Regeln |
| `06_Versioning-Change-Management` | API-Versionierung, Migrations, Changelogs |

---

## 07_Setup-Dev - Setup & Entwicklung

Installation und Entwickler-Ressourcen.

| Datei | Beschreibung |
|-------|--------------|
| `01_Admin-System` | Admin-Panel, Systemverwaltung, Konfiguration |
| `02_Setup-Wizard-Installation` | Erstinstallation, Wizard-Schritte, Konfiguration |
| `03_Developer-Guide-KI` | Entwickler-Richtlinien, Code-Standards, KI-Prompts |

---

## Wichtige Einstiegspunkte

| Ich will... | Lese... |
|-------------|---------|
| Das System verstehen | `01_Core/00_System-Übersicht` |
| Lernmethoden kennenlernen | `01_Core/02_Lernmethoden` |
| Code schreiben | `07_Setup-Dev/03_Developer-Guide-KI` |
| API nutzen | `05_Technical/02_API-Spezifikation` |
| KI-Features verstehen | `04_KI/01_KI-Pipeline` |
| System installieren | `07_Setup-Dev/02_Setup-Wizard-Installation` |

---

## Archiv

Historische Dokumente befinden sich in `Archive/`:
- `development_phases/` - Implementierungs-Phasen (PHASE-B24, PHASE-C1)
- `planning/` - Roadmaps, Konzepte
- Alte Versionen und Cleanup-Reports

---

*Letzte Aktualisierung: Dezember 2024*
