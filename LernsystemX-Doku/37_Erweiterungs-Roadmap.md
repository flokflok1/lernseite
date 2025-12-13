# 37 - Erweiterungs-Roadmap

> **Dokument-Version:** 2.0
> **Erstellt:** 2025-12-01
> **Aktualisiert:** 2025-12-03
> **Status:** In Arbeit (Phase 1 teilweise abgeschlossen)
> **Autor:** Pascal / Claude

---

## Übersicht

Dieses Dokument beschreibt die geplanten Erweiterungen für LernsystemX. Ziel ist es, die Plattform zu einer marktführenden Lernlösung auszubauen, die durch intelligentes Token-Management, Community-Content und Gamification überzeugt.

---

## 1. Flexibles Kategorie-System ✅ IMPLEMENTIERT

> **Status:** Abgeschlossen (2025-12-03)
> **Migration:** `056_flexible_categories.sql`
> **Dokumentation:** [12_Kurs-Kategorisierung-Flexibles-System.md](12_Kurs-Kategorisierung-Flexibles-System.md)

### 1.1 Was wurde umgesetzt
- ✅ Selbstreferenzierende `course_categories` Tabelle
- ✅ Unbegrenzte Tiefe (praktisches Limit: 20 Ebenen)
- ✅ Automatische Pfad-Berechnung via Trigger (`path`, `path_ids`, `root_id`)
- ✅ GIN-Index für schnelle `path_ids` Abfragen
- ✅ Multi-Language Support (DE, EN, ES, FR, PL)
- ✅ CategoryRepository mit allen CRUD-Operationen
- ✅ API-Endpunkte (Tree, Roots, By-Path, Descendants, Move)
- ✅ Admin-UI mit rekursivem Tree-View
- ✅ Level-Farben für 20 Ebenen

### 1.2 System-Überblick
**Unbegrenzte Baum-Struktur** mit selbst-referenzierenden Kategorien.

```
Kategorie → Unterkategorie → ... → Kurs → Modul
                ↑
          (beliebig tief)
```

#### Beispiel-Struktur:
```
IT
├── Netzwerk
│   ├── Cisco
│   │   ├── CCNA
│   │   ├── CCNP
│   │   └── CCIE
│   ├── CompTIA
│   │   └── Network+
│   └── Allgemein
│       ├── TCP/IP
│       └── Subnetting
├── Programmierung
│   ├── Web
│   │   ├── Frontend (HTML, JS, React...)
│   │   └── Backend (Python, Node...)
│   └── Mobile (iOS, Android)
└── Datenbanken
    ├── SQL (MySQL, PostgreSQL)
    └── NoSQL (MongoDB)

Kaufmännisch
├── Buchhaltung
├── Controlling
└── ...
```

### 1.3 Datenbank-Schema

```sql
CREATE TABLE categories (
    category_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID REFERENCES categories(category_id),  -- NULL = Root-Kategorie
    name VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    slug VARCHAR(100) UNIQUE,
    icon VARCHAR(50),
    color VARCHAR(7),           -- Hex-Farbe (#FF5733)
    description TEXT,
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,

    -- Für schnelle Abfragen (denormalisiert)
    path TEXT,                  -- "IT/Netzwerk/Cisco/CCNA"
    depth INT DEFAULT 0,        -- Tiefe im Baum (0, 1, 2, 3...)
    root_id UUID,               -- ID der Root-Kategorie

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by UUID REFERENCES users(user_id)
);

-- Index für Parent-Abfragen
CREATE INDEX idx_categories_parent ON categories(parent_id);
CREATE INDEX idx_categories_root ON categories(root_id);
CREATE INDEX idx_categories_path ON categories(path);

-- Kurse referenzieren Kategorien auf beliebiger Ebene
ALTER TABLE courses ADD COLUMN category_id UUID REFERENCES categories(category_id);
```

### 1.4 Admin-UI Features
- Drag & Drop zum Umsortieren
- Inline-Bearbeitung
- Breadcrumb-Navigation
- Bulk-Import/Export (CSV/JSON)
- Such-/Filterfunktion

---

## 2. Globaler KI-Tutor

### 2.1 Konzept
Der NPC-Tutor wird von einer Lernmethode (LM07) zu einem **globalen, persistenten Feature**.

**Ersetzt:** LM07 (NPC-Tutor als Lernmethode)
**LM07 Status:** Reserviert für zukünftige Nutzung

### 2.2 Features

| Feature | Beschreibung |
|---------|--------------|
| **Persistenter Avatar** | Unten rechts im UI, immer verfügbar |
| **Kontext-Awareness** | Weiß, wo der Schüler gerade ist |
| **Theorie-Erklärung** | Erklärt Inhalte vor Übungen |
| **Hilfe-Funktion** | Springt ein, wenn Schüler nicht weiterkommt |
| **Personalisierung** | Passt sich an Lernstil an |
| **Sprach-Support** | Text + optional Audio (TTS) |

### 2.3 UI-Konzept

```
┌────────────────────────────────────────────────────────┐
│                    Lerninhalt                          │
│                                                        │
│    [Theorie / Übung / Quiz...]                        │
│                                                        │
│                                                        │
│                                                        │
│                                        ┌─────────────┐│
│                                        │ 🤖 Tutor    ││
│                                        │ "Brauchst   ││
│                                        │  du Hilfe?" ││
│                                        └─────────────┘│
└────────────────────────────────────────────────────────┘
```

### 2.4 Tutor-Modi

| Modus | Trigger | Verhalten |
|-------|---------|-----------|
| **Passiv** | Standard | Avatar sichtbar, wartet |
| **Proaktiv** | Schüler stockt | Bietet Hilfe an |
| **Aktiv** | Schüler fragt | Antwortet auf Fragen |
| **Lehr-Modus** | Vor Übungen | Erklärt Theorie |

---

## 3. Token-Spar-System (Lokales Wissen)

### 3.1 Ziel
**95% weniger API-Kosten** nach 1-2 Jahren durch intelligentes Caching und lokale Wissensaufbau.

### 3.2 Wissens-Pyramide

```
┌─────────────────────────────────────────────┐
│  Level 3: KI-API (Anthropic/OpenAI)        │
│  → Nur wenn Level 1+2 keine Antwort haben  │
│  → Antwort wird in Level 2 gespeichert!    │
├─────────────────────────────────────────────┤
│  Level 2: Gelerntes Wissen (DB)            │
│  → Aus früheren Gesprächen gespeichert     │
│  → Semantisches Matching (Embeddings)      │
│  → Template-System für Variationen         │
├─────────────────────────────────────────────┤
│  Level 1: Statischer Content               │
│  → Definitionen, Theorie vom Creator       │
│  → Kostet NIE Tokens                       │
└─────────────────────────────────────────────┘
```

### 3.3 Semantisches Caching

Nicht nur exakte Matches, sondern **ähnliche Fragen** werden erkannt:

```
Frage 1: "Was ist DHCP?"           → Embedding [0.82, 0.1...]
Frage 2: "Erklär mir DHCP"         → Embedding [0.81, 0.1...]
Frage 3: "Wie funktioniert DHCP?"  → Embedding [0.79, 0.12.]

Similarity Score: 0.94 (> 0.85 Threshold)
→ ALLE 3 bekommen dieselbe gecachte Antwort!
```

### 3.4 Template-System

```json
{
  "topic": "dhcp",
  "base_answer": "DHCP (Dynamic Host Configuration Protocol) ist ein Netzwerkprotokoll, das automatisch IP-Adressen vergibt.",
  "variations": {
    "simple": "DHCP vergibt automatisch IP-Adressen.",
    "detailed": "[Ausführliche Erklärung mit DORA-Prozess...]",
    "with_example": "[Basis] Beispiel: Laptop kommt ins WLAN..."
  },
  "examples": [
    "Stell dir vor: Dein Laptop kommt ins WLAN...",
    "Wie ein Hotelrezeptionist, der Zimmernummern vergibt..."
  ]
}
```

### 3.5 Global Shared Wissensbasis

Alle Schulen/User teilen eine gemeinsame Wissensbasis:

```
Schule A: 500 Schüler fragen zu "Netzwerk"
Schule B: 300 Schüler fragen zu "Datenbanken"
Schule C: 400 Schüler fragen zu "Programmierung"
                    ↓
        GLOBALE TUTOR-WISSENSBASIS
                    ↓
Neue Schule D startet → Tag 1 schon 95% ohne KI!
```

### 3.6 Token-Ersparnis Timeline

| Zeitraum | Lokal | KI-API | Ersparnis |
|----------|-------|--------|-----------|
| Monat 1 | 20% | 80% | - |
| Monat 3 | 40% | 60% | 25% |
| Monat 6 | 60% | 40% | 50% |
| Monat 12 | 80% | 20% | 75% |
| Monat 24 | 95% | 5% | 94% |

### 3.7 Datenbank-Schema

```sql
-- Tutor-Wissens-Cache
CREATE TABLE tutor_knowledge (
    knowledge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_embedding VECTOR(1536),    -- OpenAI Ada Embedding
    question_pattern TEXT,            -- Ursprüngliche Frage
    answer_text TEXT NOT NULL,
    answer_template JSONB,            -- Variationen

    -- Metadaten
    category_id UUID REFERENCES categories(category_id),
    language VARCHAR(5) DEFAULT 'de',
    quality_score FLOAT DEFAULT 0.0,  -- 0-1, aus Feedback
    usage_count INT DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP,

    -- Für Deduplizierung
    content_hash VARCHAR(64) UNIQUE
);

-- Index für Vektor-Suche (pgvector)
CREATE INDEX idx_knowledge_embedding ON tutor_knowledge
USING ivfflat (topic_embedding vector_cosine_ops);
```

---

## 4. Marketplace / Creator-System

### 4.1 Wer kann Kurse erstellen?

| Rolle | Rechte | Revenue Share |
|-------|--------|---------------|
| **Academy (Admin)** | Geschützte Kurse, nur Admin bearbeitet | 100% |
| **Unternehmen** | Interne Schulungen / Marketplace | 70% |
| **Schulen** | Für Schüler / Teilen möglich | 70% |
| **Dozenten** | Verifiziert, Marketplace | 70% |
| **Creator** | Nach Moderation, Marketplace | 70% |
| **Premium User** | Eigene Materialien teilen | 70% |

### 4.2 Kurs-Typen

| Typ | Ersteller | Sichtbarkeit | Bearbeitung |
|-----|-----------|--------------|-------------|
| **Academy** | Admin | Öffentlich | Nur Admin |
| **Private** | Alle | Nur Creator | Nur Creator |
| **Organisation** | Firma/Schule | Organisation | Org-Admins |
| **Community** | Creator | Öffentlich, kostenlos | Nur Creator |
| **Marketplace** | Creator | Öffentlich, kostenpflichtig | Nur Creator |

### 4.3 Quality Control

```
Creator erstellt Kurs
        ↓
   [Entwurf]
        ↓
"Veröffentlichen" klicken
        ↓
┌─────────────────────────┐
│   MODERATION QUEUE      │
├─────────────────────────┤
│ • KI prüft auf Plagiate │
│ • KI prüft Qualität     │
│ • Moderator gibt frei   │
└─────────────────────────┘
        ↓
✅ Freigegeben → Im Marketplace
❌ Abgelehnt → Feedback an Creator
```

### 4.4 Revenue Share Modell

```
Kurs-Verkauf: 29,99€
═══════════════════

Creator:     70%  →  20,99€
Plattform:   25%  →   7,50€
Payment:      5%  →   1,50€
```

---

## 5. Dynamisches Rollen-System

### 5.1 Konzept
Rollen werden **via Admin-UI** erstellt, bearbeitet und gelöscht - nicht hardcoded.

### 5.2 System-Rollen (nicht löschbar)

| Rolle | Beschreibung |
|-------|--------------|
| **Super-Admin** | Vollzugriff auf alles |
| **Free User** | Basis-Rolle für alle |

### 5.3 Konfigurierbare Rollen

- Premium User
- Creator
- Dozent
- Schul-Admin
- Firmen-Admin
- Moderator
- Support
- Content-Manager
- *+ Beliebig erweiterbar*

### 5.4 Permission-System

```
Granulare Berechtigungen:
─────────────────────────
courses.create
courses.edit.own
courses.edit.all
courses.delete
courses.publish

users.view
users.edit
users.ban
users.delete

finance.view
finance.payout

system.settings
system.roles
...
```

### 5.5 Datenbank-Schema

```sql
-- Rollen
CREATE TABLE roles (
    role_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(7),
    icon VARCHAR(50),
    is_system BOOLEAN DEFAULT FALSE,  -- System-Rollen nicht löschbar
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Permissions
CREATE TABLE permissions (
    permission_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(100) UNIQUE NOT NULL,  -- z.B. "courses.edit.all"
    name VARCHAR(100),
    category VARCHAR(50),               -- Gruppierung im UI
    description TEXT
);

-- Rollen-Permissions Mapping
CREATE TABLE role_permissions (
    role_id UUID REFERENCES roles(role_id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permissions(permission_id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- User-Rollen (User kann mehrere Rollen haben)
CREATE TABLE user_roles (
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(role_id) ON DELETE CASCADE,
    granted_by UUID REFERENCES users(user_id),
    granted_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, role_id)
);

-- Audit-Log
CREATE TABLE role_audit_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    action VARCHAR(50),  -- 'role_assigned', 'role_removed', 'permission_changed'
    target_user_id UUID,
    target_role_id UUID,
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 5.6 Admin-UI Features

- Rollen-Matrix (Permissions pro Rolle)
- Rollen-Templates zum Kopieren
- Audit-Log (wer hat was wann geändert)
- Bulk-Zuweisung (mehrere User gleichzeitig)

---

## 6. KI-Feedback-System

### 6.1 Konzept
KI analysiert eingehendes Feedback und erstellt **priorisierte, actionable Tasks**.

### 6.2 Feedback-Quellen

- User / Schüler
- Schulen
- Dozenten / Lehrer
- Unternehmen
- Creator

### 6.3 KI-Analyse

```
Eingehendes Feedback
        ↓
┌─────────────────────────────────┐
│      KI-ANALYSE                 │
├─────────────────────────────────┤
│ • Gruppiert ähnliche Feedbacks  │
│ • Erkennt Kategorien            │
│ • Priorisiert nach Häufigkeit   │
│ • Erstellt Lösungsvorschläge    │
└─────────────────────────────────┘
        ↓
Admin-Dashboard mit Tasks
```

### 6.4 Kategorien

| Kategorie | Beispiel | Ziel |
|-----------|----------|------|
| **Bug** | "Button geht nicht" | Entwickler |
| **Content** | "Erklärung verwirrend" | Content-Team |
| **Feature** | "Wäre cool wenn..." | Produkt-Backlog |
| **Support** | "Wie mache ich..." | FAQ erweitern |
| **Lob** | "Super App!" | Marketing |

### 6.5 Admin-Dashboard

```
┌─────────────────────────────────────────────────────┐
│  FEEDBACK COCKPIT                                   │
├─────────────────────────────────────────────────────┤
│  Diese Woche: 234 Feedbacks                        │
│  → KI gruppiert zu: 18 Tasks                       │
│  → Davon kritisch: 2                               │
│  → Auto-beantwortet: 156 (67%)                    │
├─────────────────────────────────────────────────────┤
│  🔴 KRITISCH                                       │
│  #1: Subnetting-Erklärung überarbeiten            │
│      → 47 ähnliche Beschwerden                    │
│      → KI-Vorschlag: Mehr Grafiken hinzufügen     │
│                                                     │
│  🟠 WICHTIG                                        │
│  #2: Mehr Rechnungswesen-Übungen                  │
│      → 3 Schulen haben angefragt                  │
│                                                     │
│  🟡 VERBESSERUNG                                   │
│  #3: Quiz-Schwierigkeit anpassen                  │
└─────────────────────────────────────────────────────┘
```

---

## 7. Battle Mode 2.0

### 7.1 Battle-Modi

| Modus | Beschreibung | Typ |
|-------|--------------|-----|
| **Quiz Battle** | Wer antwortet schneller & korrekter? | PvP |
| **Code Battle** | Programmieraufgabe lösen | PvP |
| **Troubleshooting** | Fehler diagnostizieren | PvP |
| **Erklär-Battle** | Konzept erklären, KI bewertet | PvP |
| **Build Battle** | Netzwerk/DB aufbauen (Drag&Drop) | PvP |
| **Boss Battle** | Kapitel-Prüfung als Bossfight | Solo |

### 7.2 Ranked System

```
Bronze → Silber → Gold → Platin → Diamant → Meister → Großmeister
```

**Pro Fachgebiet!** Ein User kann sein:
- SQL: Diamant
- Netzwerk: Gold
- Programmierung: Silber

### 7.3 Turniere

| Turnier | Frequenz | Teilnehmer |
|---------|----------|------------|
| Klassen-Battle | Wöchentlich | Eine Klasse |
| Schul-Meisterschaft | Monatlich | Eine Schule |
| Regionen-Cup | Quartalsweise | Region |
| Championship | Jährlich | Alle |

### 7.4 Token-Effizienz
Battle-Aufgaben werden **vorher generiert und gecacht** - keine Live-API-Calls während Battles.

---

## 8. Implementierungs-Reihenfolge

### Phase 1: Foundation
- [x] ✅ Flexibles Kategorie-System (Baum-Struktur) - **Abgeschlossen 2025-12-03**
- [ ] Dynamisches Rollen-System
- [ ] Token-Spar-System (Wissens-Pyramide Basis)

### Phase 2: Core Features
- [ ] Globaler KI-Tutor (Avatar UI + Backend)
- [ ] LM07 reservieren
- [ ] Semantisches Caching implementieren

### Phase 3: Marketplace
- [ ] Creator-System
- [ ] Kurs-Moderation + KI-Prüfung
- [ ] Revenue Share System

### Phase 4: Engagement
- [ ] Battle Mode 2.0 (alle Modi)
- [ ] Ranked System
- [ ] Turniere

### Phase 5: Optimization
- [ ] KI-Feedback-System
- [ ] Advanced Analytics
- [ ] Performance & Scaling

---

## 9. Offene Fragen

- [ ] LM07: Reserviert oder neue Funktion?
- [ ] Battle Mode: Welche Modi zuerst?
- [ ] Marketplace: Ab welcher User-Zahl starten?

---

## Changelog

| Version | Datum | Änderungen |
|---------|-------|------------|
| 1.0 | 2025-12-01 | Initiale Version |
| 2.0 | 2025-12-03 | Flexibles Kategorie-System als implementiert markiert |
