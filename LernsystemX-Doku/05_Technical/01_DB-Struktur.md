# 01 – Datenbankstruktur (GBA Edition)

**Version:** 2.0 (Group-Based Architecture)
**Stand:** 2026-01-25
**Status:** Production Ready

---

## Überblick

Die LSX Datenbank implementiert **Group-Based Architecture (GBA)** für flexible Zugriffskontrolle.

### Unterstützte Funktionen
- 👥 **Gruppen-Management** (core.groups, core.users_groups) - Flexible Organisationsstruktur
- 🔐 **Berechtigungen** (core.permissions, core.group_permissions) - Granular access control
- 📚 **Kurssystem** - Kurse, Kapitel, Lektionen mit 12 Content-Lernmethoden (LM00-LM11)
- 🤖 **KI-Pipeline** - Multi-provider AI integration, Token-Verbrauch
- 🌐 **Community** - Social network, Posts, Comments, Followers
- 💰 **Billing** - Token-basiertes Prämiensystem
- 📊 **Analytics** - Dashboard, Widgets, User Tracking
- 🎥 **LiveRoom** - WebRTC, Whiteboard, Recordings
- 🌍 **Internationalisierung** - 20+ Sprachen

---

## Kernarchitektur

### 📊 Datenbank-Ökosystem

```
┌─────────────────────────────────────────────────────────┐
│                    PostgreSQL 16                        │
│              (153 Tabellen, 66 Migrations)              │
└─────────────────────────────────────────────────────────┘

┌─── SCHEMA: core ─────────────────────────────────────┐
│ Benutzerverwaltung & GBA                             │
│ • users                                              │
│ • groups (GBA - organisiert Benutzer)               │
│ • users_groups (Zugehörigkeit)                       │
│ • permissions (Berechtigungsdefinitionen)            │
│ • role_permissions (Zuordnung)                       │
│ • organizations                                      │
│ • organizations_members                              │
└──────────────────────────────────────────────────────┘

┌─── SCHEMA: courses ──────────────────────────────────┐
│ Kursmanagenent                                       │
│ • courses                                            │
│ • chapters                                           │
│ • lessons                                            │
│ • learning_method_instances (LM00-LM11)             │
│ • lesson_content                                     │
└──────────────────────────────────────────────────────┘

┌─── SCHEMA: support_systems ──────────────────────────┐
│ 25 System-Features                                   │
│ • system_features (Audio, Collaboration, etc.)      │
│ • course_system_features (Zuordnung)                │
└──────────────────────────────────────────────────────┘

┌─── SCHEMA: ai_pipeline ──────────────────────────────┐
│ KI-Integration & Jobs                                │
│ • ai_models, ai_providers                            │
│ • ai_jobs, ai_job_results                            │
│ • ai_requests, ai_outputs                            │
│ • prompts, prompt_categories                         │
└──────────────────────────────────────────────────────┘

┌─── SCHEMA: community ────────────────────────────────┐
│ Social Network (Community Groups)                     │
│ • groups (Community-Gruppen - anders als core.groups)│
│ • group_members                                      │
│ • posts, comments, likes                             │
│ • followers                                          │
└──────────────────────────────────────────────────────┘

┌─── SCHEMA: billing ──────────────────────────────────┐
│ Token & Abrechnung                                   │
│ • token_wallets (Benutzer-Tokenguthaben)           │
│ • token_transactions                                 │
│ • subscriptions                                      │
│ • premium_features                                   │
└──────────────────────────────────────────────────────┘

┌─── SCHEMA: analytics ────────────────────────────────┐
│ Dashboard & Widgets                                  │
│ • dashboards, dashboard_widgets                      │
│ • user_analytics, course_analytics                   │
│ • widget_registry, widget_configurations             │
└──────────────────────────────────────────────────────┘

┌─── SCHEMA: liveroom ─────────────────────────────────┐
│ WebRTC & Streaming                                   │
│ • liverooms, liveroom_participants                   │
│ • whiteboard, recordings                             │
│ • chat_messages, reactions                           │
└──────────────────────────────────────────────────────┘

┌─── SCHEMA: notifications ────────────────────────────┐
│ Benachrichtigungssystem                              │
│ • notifications, notification_preferences            │
│ • notification_templates                             │
└──────────────────────────────────────────────────────┘

┌─── SCHEMA: translations ─────────────────────────────┐
│ Internationalisierung                                │
│ • translations (i18n Cache)                          │
│ • translation_strings                                │
│ • supported_languages                                │
└──────────────────────────────────────────────────────┘
```

---

## Group-Based Architecture (GBA)

### 🔑 Kernkonzept

**Gruppen** sind die zentrale Organisationseinheit:
- Benutzer gehören zu einer oder mehreren **Gruppen**
- Jede Gruppe hat **Berechtigungen** (permissions)
- Berechtigungen steuern **API-Zugriff** und **UI-Funktionalität**

### 📋 Kernentitäten

#### `core.groups` - Gruppendefinition
```sql
CREATE TABLE core.groups (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) UNIQUE,           -- z.B. "system-admin", "teacher", "student"
  slug VARCHAR(100) UNIQUE,           -- z.B. "system_admin", "teacher", "student"
  description TEXT,
  group_type VARCHAR(50),             -- "system", "organization", "custom"
  frontend_role VARCHAR(100),         -- "Admin", "Teacher", "Student", etc.
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP
);
```

#### `core.users_groups` - Zugehörigkeit
```sql
CREATE TABLE core.users_groups (
  user_id UUID REFERENCES core.users(user_id),
  group_id INTEGER REFERENCES core.groups(id),
  member_role VARCHAR(50),            -- "owner", "moderator", "member"
  joined_at TIMESTAMP DEFAULT NOW(),
  left_at TIMESTAMP NULL,
  is_active BOOLEAN DEFAULT TRUE,
  PRIMARY KEY (user_id, group_id)
);
```

#### `core.permissions` - Berechtigungsdefinitionen
```sql
CREATE TABLE core.permissions (
  id SERIAL PRIMARY KEY,
  permission_code VARCHAR(100) UNIQUE, -- z.B. "admin:system", "manage:courses"
  description TEXT,
  resource VARCHAR(100),               -- "admin", "courses", "users"
  action VARCHAR(50),                  -- "create", "read", "update", "delete"
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### `core.role_permissions` - Zuordnung
```sql
CREATE TABLE core.role_permissions (
  group_id INTEGER REFERENCES core.groups(id),
  permission_id INTEGER REFERENCES core.permissions(id),
  PRIMARY KEY (group_id, permission_id)
);
```

### 🔄 Berechtigungsauflösung

SQL-Funktion `get_user_effective_permissions(user_id)`:

```sql
SELECT DISTINCT permission_code
FROM core.permissions p
JOIN core.role_permissions rp ON p.id = rp.permission_id
JOIN core.groups g ON rp.group_id = g.id
JOIN core.users_groups ug ON g.id = ug.group_id
WHERE ug.user_id = $1
  AND ug.is_active = TRUE
  AND g.is_active = TRUE
  AND rp.is_active = TRUE;
```

**Ablauf:**
1. Benutzer Login → Gruppen-Abfrage
2. JWT Token beinhaltet: `groups: [{ id, name, slug, type, permissions: [...] }]`
3. Frontend nutzt `groups` für UI-Entscheidungen
4. Backend validiert mit Decorator: `@require_permission('admin:system')`

---

## Prämiensystem (Token-Based)

### `billing.token_wallets` - Tokenguthaben
```sql
CREATE TABLE billing.token_wallets (
  user_id UUID PRIMARY KEY REFERENCES core.users(user_id),
  balance INTEGER DEFAULT 0,          -- Token-Saldo (0 = Free Tier)
  tier VARCHAR(50) DEFAULT 'free',    -- free, premium, creator, enterprise
  monthly_limit INTEGER,               -- Monatliches Limit (NULL = unbegrenzt)
  reset_date DATE,                    -- Wenn monthly_limit gesetzt
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### `billing.token_transactions` - Transaktionen
```sql
CREATE TABLE billing.token_transactions (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES core.users(user_id),
  amount INTEGER,                     -- Positiv = Kauf, Negativ = Verbrauch
  type VARCHAR(50),                   -- "purchase", "usage", "refund"
  reason VARCHAR(255),                -- z.B. "AI text generation"
  source VARCHAR(100),                -- "stripe", "paypal", "api_call"
  reference_id VARCHAR(255),          -- z.B. Transaction-ID
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Lernmethoden (Content-LMs)

### Constraint: Genau 12 Lernmethoden

```sql
-- learning_methods.method_type MUST zwischen 0-11
ALTER TABLE learning_methods
ADD CONSTRAINT chk_method_type CHECK (method_type >= 0 AND method_type <= 11);

-- Nur 3 Gruppen erlaubt
ALTER TABLE learning_methods
ADD CONSTRAINT chk_group_code CHECK (group_code IN ('A', 'B', 'C'));
```

### 🎯 Die 12 Lernmethoden

| ID | Name | Gruppe | Fokus |
|:--:|------|:------:|-------|
| LM00 | Text-Lektion | A | Theorie |
| LM01 | Video-Lektion | A | Erklärfilm |
| LM02 | Interaktive Erklärung | A | Visualisierung |
| LM03 | KI-Tutorium | A | Personalisiert |
| LM04 | Oral Explanation | A | Sprachlich |
| LM05 | Übungsaufgaben | B | Anwenden |
| LM06 | Code Sandbox | B | IT-Praxis |
| LM07 | Whiteboard | B | Interaktiv |
| LM08 | Quiz | B | Feedback |
| LM09 | Exam | C | Prüfung |
| LM10 | Case Study | C | Analyse |
| LM11 | Peer Review | C | Feedback |

---

## System-Features (25 Features)

### `support_systems.system_features` - Feature-Registry

```sql
CREATE TABLE support_systems.system_features (
  id SERIAL PRIMARY KEY,
  feature_code VARCHAR(100) UNIQUE,   -- z.B. "whiteboard_engine"
  feature_name VARCHAR(255),          -- z.B. "Whiteboard Engine"
  description TEXT,
  category VARCHAR(50),               -- "audio", "collaboration", "exam_systems", etc.
  requires_infrastructure BOOLEAN,
  requires_external_service BOOLEAN,
  icon VARCHAR(255),
  former_lm_id INTEGER NULL,          -- Falls vorher LM war
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 🎯 25 System-Features (Kategorien)

- **audio** (2): TTS, Speech Recognition
- **collaboration** (3): Chat, Video Call, Whiteboard
- **exam_systems** (2): IHK Exam, Adaptive Testing
- **gamification** (3): XP System, Badges, Leaderboards
- **interactive_tools** (4): Formula Editor, Graph Plotter, Code Sandbox, Scientific Calculator
- **it_environments** (2): Cloud IDE, Docker Lab
- **learning_paths** (2): Skill Trees, Adaptive Paths
- **meta_features** (2): Analytics, Progress Tracking
- **tutor** (2): NPC Tutor, Live Tutor
- **visualization** (1): 3D Models

---

## Community (Social Network)

### Unterschied: `core.groups` vs `community.groups`

| Ort | Zweck | Beispiele |
|:----:|-------|-----------|
| **core.groups** | Access Control (GBA) | system-admin, teacher, student |
| **community.groups** | Social Network | Python Learners, Game Dev Club |

### `community.groups` - Community-Gruppen

```sql
CREATE TABLE community.groups (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255),
  description TEXT,
  owner_id UUID REFERENCES core.users(user_id),
  is_public BOOLEAN DEFAULT FALSE,
  member_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### `community.posts` - Social Feed

```sql
CREATE TABLE community.posts (
  id SERIAL PRIMARY KEY,
  author_id UUID REFERENCES core.users(user_id),
  group_id INTEGER REFERENCES community.groups(id),
  content TEXT,
  attachments JSONB,
  like_count INTEGER DEFAULT 0,
  comment_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP
);
```

---

## Checkliste für GBA-Konformität

- ✅ Alle Benutzer haben mindestens eine Gruppe (`core.users_groups`)
- ✅ Alle Gruppen haben klar definierte Berechtigungen (`core.permissions`)
- ✅ JWT Token enthält `groups` Claim mit Berechtigungen
- ✅ API Decorators prüfen Berechtigungen aus JWT
- ✅ Community-Gruppen sind NICHT das gleiche wie Access-Control Gruppen
- ✅ Keine Referenzen zu veraltetem RBAC oder RoleStudio
- ✅ UserRole Enum nur für Billing Tiers (Legacy)
- ✅ Learning Methods: Genau 12 (LM00-LM11), method_type 0-11, group_code A-C

---

**Stand:** 2026-01-25 | **Version:** 2.0 | **Status:** Production
