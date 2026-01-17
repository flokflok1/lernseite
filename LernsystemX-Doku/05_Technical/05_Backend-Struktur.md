# 17 – Backend-Struktur (Final) v3.2

**Version:** 3.2
**Stand:** 16.01.2026
**Änderungen:** URL Paths: /admin/ → /admin-panel/ (Semantic Clarity) + Admin Panel Reorganization (Settings-based Structure) + Complete Enterprise Architecture + AI Editor APIs + Compliance GDPR APIs + Error/WebSocket Standardisierung

---

## Überblick

Dieses Dokument beschreibt die komplette **Enterprise-Grade Backend-Architektur** des LSX Lernsystems.

Das Backend ist **modular**, **sicher**, **skalierbar**, **vollständig compliance-konform**, **feature-flag-gesteuert** und **mit AI Editor integriert**.

### 🎯 Neue Features in v3.2

- ✅ **Semantic URL Paths** - `/admin/` → `/admin-panel/` (Clarity: Interface vs. Role)
- ✅ **Admin Panel Reorganization** - Settings-based Structure (Sidebar-aligned)
- ✅ **AI Editor System** - Chat, Content Generation, Variants, Sessions
- ✅ **Compliance APIs** - GDPR Data Export/Deletion, Privacy Controls, Age Verification
- ✅ **Feature Flag System** - Progressive Rollout (5% → 25% → 100%)
- ✅ **Social Learning Network** - Posts, Feed, Follow, Likes, Comments
- ✅ **Full Compliance** - DSA, NetzDG, GDPR, ISO 27001, Child Safety
- ✅ **Content Moderation** - AI + Human, 24h/7d Response Times, SLA Monitor
- ✅ **DRM System** - Denuvo-style Protection
- ✅ **WebSocket Events** - Standardized real-time events
- ✅ **Error Response Format** - Standardized error codes & messages
- ✅ **Internationalization** - 20+ Languages

### 🛠️ Tech-Stack

| Technologie | Verwendung |
|------------|-----------|
| 🐍 **Python 3.12+** | Core Language |
| 🌶️ **Flask 3.0** | Web Framework (Blueprint-Architektur) |
| 🗃️ **psycopg 3** | PostgreSQL-Treiber mit Connection Pooling (**KEIN ORM**) |
| 🐘 **PostgreSQL** | Datenbank |
| 🔴 **Redis** | Caching, Rate Limits, Sessions, Celery Queue, Feature Flags |
| 📦 **Celery** | Background Tasks (KI-Pipeline, Moderation) |
| 🔌 **Flask-SocketIO** | WebSockets / Real-time (LiveRoom, Notifications) |
| 🎥 **WebRTC** | Video/Audio (mediasoup/Jitsi) |
| 🔑 **JWT** | Authentication (Flask-JWT-Extended) |
| 📋 **Pydantic** | Request/Response Validation |
| 🤖 **AI Moderation** | OpenAI Moderation API, Perspective API |
| 🔒 **Cryptography** | AES-256-GCM, RSA-4096 (DRM) |

> ⚠️ **WICHTIG:** Dieses Projekt verwendet **KEIN ORM** (kein SQLAlchemy). Alle Datenbankoperationen erfolgen über direktes SQL mit psycopg und dem Repository-Pattern.

---

## 1. System-Architektur (C4 Model - Context)

```mermaid
graph TB
    subgraph "Externe Systeme"
        USER[👤 Frontend User]
        ADMIN[👑 Admin]
        MODERATOR[👮 Moderator]
        KI_API[🤖 KI APIs<br/>Anthropic/OpenAI]
        MODERATION_API[🛡️ Moderation APIs<br/>OpenAI/Perspective]
        WEBRTC[🎥 WebRTC Server<br/>mediasoup/Jitsi]
        AUTHORITIES[🏛️ Authorities<br/>BKA/NCMEC]
    end

    subgraph "LSX Backend System"
        API[🌶️ Flask API<br/>REST Endpoints]
        CELERY[📦 Celery Workers<br/>Background Tasks]
        SOCKET[🔌 WebSocket Server<br/>Flask-SocketIO]
        MODERATION[🛡️ Content Moderation<br/>AI + Human]
        FEATURE_FLAGS[🎚️ Feature Flag System<br/>Progressive Rollout]
        STUDIO[🎨 AI Editor<br/>Content Generation]

        subgraph "Data Layer"
            DB[(🐘 PostgreSQL<br/>psycopg3 Pool)]
            REDIS[(🔴 Redis<br/>Cache/Queue/Flags)]
            STORAGE[📁 File Storage<br/>S3/Local]
        end
    end

    USER -->|HTTP/JSON| API
    USER -->|Social Features| API
    ADMIN -->|HTTP/JSON| API
    MODERATOR -->|Moderation| MODERATION
    USER -->|WebSocket| SOCKET

    API -->|Feature Check| FEATURE_FLAGS
    API -->|Direct SQL| DB
    API -->|Cache/Rate Limit| REDIS
    API -->|Queue Tasks| CELERY
    API -->|Studio Operations| STUDIO

    FEATURE_FLAGS -->|Cache| REDIS
    MODERATION -->|AI Analysis| MODERATION_API
    MODERATION -->|Report CSAM| AUTHORITIES

    CELERY -->|Direct SQL| DB
    CELERY -->|KI Requests| KI_API
    CELERY -->|Store Results| STORAGE
    CELERY -->|Moderation| MODERATION_API

    SOCKET -->|Pub/Sub| REDIS
    SOCKET -->|Signaling| WEBRTC
    SOCKET -->|Notifications| REDIS

    STUDIO -->|KI Requests| KI_API
    STUDIO -->|Store Content| STORAGE

    style DB fill:#336791,color:#fff
    style REDIS fill:#DC382D,color:#fff
    style API fill:#3776AB,color:#fff
    style MODERATION fill:#FF6B6B,color:#fff
    style STUDIO fill:#9C27B0,color:#fff
```

---

## 1.5 System-Features vs. Content-Lernmethoden (LMS Architecture)

### Wichtige Unterscheidung

Das LernSystemX unterscheidet zwischen zwei Typen von Lernfunktionalität:

#### **Content-Lernmethoden (12 LMs)**
- **Was:** Aufgabenformate für Lerninhalt (Flashcards, Quiz, Lückentext, etc.)
- **Wo:** `learning_methods.py` Blueprint
- **Dokumentation:** `01_Core/02_Lernmethoden.md`
- **Struktur:** JSONB-Content pro Kapitel/Lektion
- **Beispiele:** LM00-LM04 (Erklärend), LM05-LM08 (Praxis), LM09-LM11 (Prüfung)

#### **System-Features (25 Features)**
- **Was:** Tools & Services mit eigener Infrastruktur
- **Wo:** Separate Module wie `exam_simulations/`, `math_toolkit/`, `tts/`, etc.
- **Dokumentation:** `01_Core/02a_System-Features.md`
- **Struktur:** Vollständige Blueprint-Module mit Repositories, Services, Models
- **Beispiele:** Whiteboard, IHK Exam System, NPC Tutor, Code Sandbox, Gamification

### System-Features im Backend (/api/v1/)

**LMS-bezogene System-Features:**

| Feature | Module | Beschreibung |
|---------|--------|-------------|
| **Exam Simulations** | `/exam_simulations/` | IHK-Exam System, praktische Prüfungen, Kompetenzchecks |
| **Math Toolkit** | `/math_toolkit/` | Mathematische Tools, Übungen, Referenz |
| **Course Editor** | `/course_editor/` | Manueller Content-Editor, AI-gestützter Editor |
| **TTS (Text-to-Speech)** | `/tts/` | Sprachausgabe, Audio-Generierung, Aussprache |
| **Feature Flags** | `/features/` | Progressive Rollout, A/B Testing, Feature Control |
| **Gamification** | `/gamification/` | XP, Badges, Quests, Achievements |

**Infrastruktur-Features:**

| Feature | Modul | Beschreibung |
|---------|-------|-------------|
| **Compliance** | `/compliance/` | GDPR, Datenschutz, Consent Management |
| **Moderation** | `/moderation/` | Content Moderation, Reports, Actions |
| **Analytics** | `/analytics/` | User Analytics, Learning Analytics, Insights |
| **Social** | `/social/` | Posts, Feed, Follow, Likes, Comments, Sharing |
| **AI/Tutor** | `/tutor/`, `/ai/` | AI Tutor, Smart Agents, Content Generation |
| **Admin Panel** | `/admin-panel/` | Settings, Course Management, User Management |

### Integration im System (Zwei-Schicht-Architektur)

#### **Schicht 1: Python-Registry (Source of Truth)**

Zentrale Definition aller 25 System-Features mit vollständiger Konfiguration:

```python
# app/ki/system_features_mapping.py
SYSTEM_FEATURES: Dict[str, SystemFeatureDefinition] = {
    "whiteboard_engine": SystemFeatureDefinition(
        feature_code="whiteboard_engine",
        feature_name="Whiteboard-Engine",
        category="interactive_tools",
        requires_infrastructure=True,
        requires_external_service=True,
        default_config={...}
    ),
    "ihk_exam_system": SystemFeatureDefinition(...),
    # ... insgesamt 25 Features
}

# Hilfs-Funktionen
get_system_feature(feature_code: str) -> SystemFeatureDefinition
get_feature_default_config(feature_code: str) -> dict
is_valid_feature_code(feature_code: str) -> bool
```

**→ Definiert: Infra-Anforderungen, Konfigurationen, Icons, Kategorien**

---

#### **Schicht 2: Datenbank-Integration (Runtime)**

System-Features werden beim Setup aus der Python-Registry in die Datenbank gepflanzt:

```python
# app/setup/seeds_config.py
SeedDataConfig.seed_system_features()  # Seeds 25 Features in die DB
```

Abfrage zur Laufzeit:

```sql
-- Alle System-Features registriert
SELECT feature_code, feature_name, category FROM support_systems.system_features;

-- Beispiel Ergebnisse:
-- whiteboard_engine | Whiteboard-Engine | interactive_tools
-- ihk_exam_system | IHK-Prüfungssystem | exam_systems
-- speech_to_text | Speech-to-Text Engine | audio
-- xp_quest_system | XP & Quest System | gamification
```

---

#### **Integration in Kursen: Feature-Level Kontrolle**

```python
# Kurse können Features auf Kapitel-Ebene aktivieren/deaktivieren
course.enable_feature("whiteboard_engine", chapter_id="ch001")
course.disable_feature("ihk_exam_system")

# Abfrage: Welche Features sind in diesem Kurs aktiv?
SELECT * FROM support_systems.system_features sf
JOIN course_features cf ON sf.feature_code = cf.feature_code
WHERE cf.course_id = 'course123'
```

### Deployment-Struktur

**WICHTIG:** Es gibt **KEINEN zentralen `/system-features/` Ordner**. System-Features sind **über /api/v1/ verteilt** als einzelne Ordner/Module:

```yaml
# AKTUELLE STRUKTUR: System-Features sind verteilt über /api/v1/

/app/api/v1/
├── /exam_simulations/     ← 🔧 System-Feature (Exam System)
├── /math_toolkit/         ← 🔧 System-Feature (Math Tools)
├── /tts/                  ← 🔧 System-Feature (Text-to-Speech)
├── /tutor/                ← 🔧 System-Feature (AI Tutor)
├── /features/             ← 🔧 System-Feature (Feature Flags)
├── /gamification/         ← 🔧 System-Feature (XP, Badges, Quests)
├── /course_editor/        ← 🔧 System-Feature (Content Editing)
├── /ai/                   ← Teils System-Feature (AI Services)
├── /social/               ← 🔧 System-Feature (Posts, Feed, Follow)
├── /community/            ← 🔧 System-Feature (Groups, Forums)
├── /messaging/            ← 🔧 System-Feature (Direct Messages)
├── /learning_methods/     ← NICHT System-Feature (12 Content-LMs)
├── /admin-panel/          ← Admin Operations
├── /profile/              ← User Profile
└── ... weitere Core APIs
```

**Registrierung:** Alle System-Features werden in der Datenbank registriert:
```sql
SELECT feature_code, feature_name FROM support_systems.system_features
ORDER BY category;

-- Ergebnis: 25 Features in 10 Kategorien (database-backed, nicht im Dateisystem organisiert)
```

---

## 2. Projektstruktur (Backend-Verzeichnis) - UPDATED

```
/backend
├── /app
│   ├── __init__.py              # 🏭 Factory Pattern (create_app)
│   ├── config.py                # ⚙️ Configuration
│   ├── extensions.py            # 🔌 Flask Extensions
│   │
│   ├── /core                    # 🎯 CORE SYSTEM
│   │   ├── /feature_flags       # ⭐ Feature Flag System
│   │   │   ├── __init__.py
│   │   │   ├── flag_manager.py
│   │   │   ├── flag_decorators.py
│   │   │   ├── flag_middleware.py
│   │   │   └── flag_admin.py
│   │   │
│   │   ├── /rollout
│   │   │   ├── percentage_rollout.py
│   │   │   ├── user_segments.py
│   │   │   ├── org_rollout.py
│   │   │   └── ab_testing.py
│   │   │
│   │   └── /configuration
│   │       ├── feature_config.py
│   │       └── rollout_config.py
│   │
│   ├── /api                     # 🌐 REST API LAYER
│   │   ├── /v1
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── # Core API (Public)
│   │   │   ├── auth.py              # /api/v1/auth
│   │   │   ├── users.py             # /api/v1/users
│   │   │   ├── profile.py           # /api/v1/profile
│   │   │   ├── courses.py           # /api/v1/courses
│   │   │   ├── categories.py        # /api/v1/categories
│   │   │   ├── learning_methods.py  # /api/v1/learning-methods
│   │   │   ├── subscriptions.py     # /api/v1/subscriptions
│   │   │   ├── tokens.py            # /api/v1/tokens
│   │   │   ├── organisations.py     # /api/v1/organisations
│   │   │   ├── health.py            # /health
│   │   │   │
│   │   │   ├── /dashboard
│   │   │   │   ├── __init__.py
│   │   │   │   ├── widgets.py
│   │   │   │   └── recommendations.py
│   │   │   │
│   │   │   ├── # Content API
│   │   │   ├── chapter_theory.py
│   │   │   ├── lesson_explanations.py
│   │   │   ├── lesson_videos.py
│   │   │   ├── exam_simulations.py               # 🔧 System-Feature: Exam System
│   │   │   │
│   │   │   ├── # KI/Tutor API
│   │   │   ├── tutor.py                          # 🔧 System-Feature: AI Tutor
│   │   │   ├── agents.py
│   │   │   ├── audio.py
│   │   │   ├── tts.py                            # 🔧 System-Feature: Text-to-Speech
│   │   │   ├── math_toolkit.py                   # 🔧 System-Feature: Math Tools
│   │   │   │
│   │   │   ├── # Analytics API
│   │   │   ├── analytics.py
│   │   │   ├── org_analytics.py
│   │   │   ├── feedback.py
│   │   │   │
│   │   │   ├── /social          # 🌟 SOCIAL API (Feature-Flagged) | 🔧 System-Feature
│   │   │   │   ├── __init__.py
│   │   │   │   ├── posts.py             # 🚩 FLAG: 'user_posts'
│   │   │   │   ├── feed.py              # 🚩 FLAG: 'feed_system'
│   │   │   │   ├── follow.py            # 🚩 FLAG: 'follow_system'
│   │   │   │   ├── likes.py             # 🚩 FLAG: 'likes_reactions'
│   │   │   │   ├── comments.py          # 🚩 FLAG: 'comments'
│   │   │   │   ├── shares.py            # 🚩 FLAG: 'content_sharing'
│   │   │   │   ├── trending.py          # 🚩 FLAG: 'trending_discovery'
│   │   │   │   ├── hashtags.py          # 🚩 FLAG: 'hashtags'
│   │   │   │   └── mentions.py          # 🚩 FLAG: 'mentions'
│   │   │   │
│   │   │   ├── /compliance      # ⭐ GDPR COMPLIANCE APIs (NEW) | 🔧 System-Feature
│   │   │   │   ├── __init__.py
│   │   │   │   ├── privacy.py           # GET/PUT /api/v1/compliance/privacy
│   │   │   │   ├── cookies.py           # GET/PUT /api/v1/compliance/cookies
│   │   │   │   ├── consent.py           # GET /api/v1/compliance/consent
│   │   │   │   ├── data_export.py       # POST /api/v1/compliance/data-export
│   │   │   │   ├── data_deletion.py     # POST /api/v1/compliance/data-deletion
│   │   │   │   ├── consent_history.py   # GET /api/v1/compliance/consent-history
│   │   │   │   └── parental_consent.py  # POST /api/v1/compliance/parental-consent
│   │   │   │
│   │   │   ├── /moderation      # 🛡️ MODERATION APIs | 🔧 System-Feature
│   │   │   │   ├── __init__.py
│   │   │   │   ├── reports.py           # POST /api/v1/moderation/reports
│   │   │   │   ├── queue.py             # GET /api/v1/moderation/queue
│   │   │   │   ├── actions.py           # POST /api/v1/moderation/actions
│   │   │   │   ├── statistics.py        # GET /api/v1/moderation/statistics
│   │   │   │   ├── sla_monitor.py       # GET /api/v1/moderation/sla-monitor (NEW)
│   │   │   │   └── appeals.py           # GET /api/v1/moderation/appeals
│   │   │   │
│   │   │   ├── /admin           # 👑 ADMIN API (Sidebar-aligned Structure) ⭐ v3.1
│   │   │   │   ├── __init__.py
│   │   │   │   │
│   │   │   │   ├── /settings    # ⚙️ SETTINGS (All Admin Settings)
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   │
│   │   │   │   │   ├── /ai      # 🤖 AI Configuration
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── jobs_creation.py        # POST /api/v1/admin-panel/settings/ai/jobs
│   │   │   │   │   │   ├── jobs_finalization.py    # PUT /api/v1/admin-panel/settings/ai/jobs/:id/finalize
│   │   │   │   │   │   ├── jobs_management.py      # GET /api/v1/admin-panel/settings/ai/jobs
│   │   │   │   │   │   ├── models_crud.py          # CRUD /api/v1/admin-panel/settings/ai/models
│   │   │   │   │   │   ├── models_defaults.py      # GET /api/v1/admin-panel/settings/ai/models/defaults
│   │   │   │   │   │   ├── models_sync.py          # POST /api/v1/admin-panel/settings/ai/models/sync
│   │   │   │   │   │   ├── models_usage.py         # GET /api/v1/admin-panel/settings/ai/models/usage
│   │   │   │   │   │   ├── ai_pricing.py           # GET /api/v1/admin-panel/settings/ai/pricing
│   │   │   │   │   │   ├── ai_model_profiles.py    # CRUD /api/v1/admin-panel/settings/ai/profiles
│   │   │   │   │   │   ├── providers_api_keys.py   # PUT /api/v1/admin-panel/settings/ai/providers/:id/api-key
│   │   │   │   │   │   ├── providers_crud.py       # CRUD /api/v1/admin-panel/settings/ai/providers
│   │   │   │   │   │   ├── providers_health.py     # GET /api/v1/admin-panel/settings/ai/providers/:id/health
│   │   │   │   │   │   └── providers_testing.py    # POST /api/v1/admin-panel/settings/ai/providers/:id/test
│   │   │   │   │   │
│   │   │   │   │   ├── /system  # 🛠️ System Settings
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── settings.py             # GET/PUT /api/v1/admin-panel/settings/system
│   │   │   │   │   │   ├── system_info.py          # GET /api/v1/admin-panel/settings/system/info
│   │   │   │   │   │   └── system_stats.py         # GET /api/v1/admin-panel/settings/system/stats
│   │   │   │   │   │
│   │   │   │   │   ├── /permissions  # 🔐 Permissions & Roles
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── roles.py                # CRUD /api/v1/admin-panel/settings/permissions/roles
│   │   │   │   │   │   └── permission_thresholds.py # GET/PUT /api/v1/admin-panel/settings/permissions
│   │   │   │   │   │
│   │   │   │   │   └── /feature_flags  # 🎚️ Feature Flags
│   │   │   │   │       ├── __init__.py
│   │   │   │   │       ├── flags.py                # CRUD /api/v1/admin-panel/settings/feature-flags/flags
│   │   │   │   │       ├── rollout.py              # PUT /api/v1/admin-panel/settings/feature-flags/rollout
│   │   │   │   │       └── analytics.py            # GET /api/v1/admin-panel/settings/feature-flags/analytics
│   │   │   │   │
│   │   │   │   ├── /audit_logs  # 📋 Audit Logs (Top-Level)
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── audit_logs.py               # GET /api/v1/admin-panel/audit-logs
│   │   │   │   │
│   │   │   │   ├── /courses    # 📚 Course Management (Top-Level)
│   │   │   │   │   ├── courses.py
│   │   │   │   │   ├── chapters.py
│   │   │   │   │   ├── lessons.py
│   │   │   │   │   ├── exams.py
│   │   │   │   │   ├── course_prompts.py
│   │   │   │   │   └── course_files.py
│   │   │   │   │
│   │   │   │   ├── /moderation  # 🛡️ Moderation Panel (Top-Level)
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── queue.py
│   │   │   │   │   ├── actions.py
│   │   │   │   │   ├── reports.py
│   │   │   │   │   ├── statistics.py
│   │   │   │   │   └── transparency.py
│   │   │   │   │
│   │   │   │   ├── dashboard.py         # GET /api/v1/admin-panel/dashboard
│   │   │   │   ├── users.py
│   │   │   │   ├── analytics.py
│   │   │   │   ├── prompts.py
│   │   │   │   ├── learning_methods.py
│   │   │   │   ├── lm_routing.py
│   │   │   │   ├── course_analytics.py
│   │   │   │   ├── course_ai_settings.py
│   │   │   │   └── course_authoring.py
│   │   │   │
│   │   │   └── /ai
│   │   │       ├── __init__.py
│   │   │       └── ai_course_generator.py
│   │   │
│   │   └── /studio              # ⭐ AI EDITOR API (NEW)
│   │       ├── __init__.py
│   │       ├── chat.py               # POST /api/v1/studio/chat
│   │       ├── generate.py           # POST /api/v1/studio/generate
│   │       ├── projects.py           # GET /api/v1/studio/projects
│   │       ├── sessions.py           # GET /api/v1/studio/sessions/:id
│   │       ├── variants.py           # POST /api/v1/studio/variants
│   │       ├── templates.py          # GET /api/v1/studio/templates
│   │       └── history.py            # GET /api/v1/studio/history
│   │
│   ├── /social                  # 🌟 SOCIAL LAYER (Complete)
│   │   ├── __init__.py
│   │   ├── /posts
│   │   │   ├── __init__.py
│   │   │   ├── post_manager.py
│   │   │   ├── post_types.py
│   │   │   ├── media_handler.py
│   │   │   ├── draft_manager.py
│   │   │   ├── scheduled_posts.py
│   │   │   └── post_analytics.py
│   │   ├── /feed
│   │   │   ├── __init__.py
│   │   │   ├── feed_generator.py
│   │   │   ├── chronological_feed.py
│   │   │   ├── algorithm_feed.py
│   │   │   ├── feed_ranking.py
│   │   │   ├── feed_cache.py
│   │   │   └── feed_disclosure.py
│   │   ├── /follow
│   │   │   ├── __init__.py
│   │   │   ├── follow_manager.py
│   │   │   ├── followers_service.py
│   │   │   ├── following_service.py
│   │   │   ├── suggestions.py
│   │   │   └── privacy_controls.py
│   │   ├── /engagement
│   │   │   ├── __init__.py
│   │   │   ├── likes.py
│   │   │   ├── reactions.py
│   │   │   ├── comments.py
│   │   │   ├── replies.py
│   │   │   ├── shares.py
│   │   │   └── bookmarks.py
│   │   ├── /profiles
│   │   │   ├── __init__.py
│   │   │   ├── profile_manager.py
│   │   │   ├── bio.py
│   │   │   ├── avatar.py
│   │   │   ├── banner.py
│   │   │   ├── portfolio.py
│   │   │   ├── achievements.py
│   │   │   ├── stats.py
│   │   │   └── privacy_settings.py
│   │   ├── /discovery
│   │   │   ├── __init__.py
│   │   │   ├── trending.py
│   │   │   ├── explore.py
│   │   │   ├── recommendations.py
│   │   │   ├── hashtags.py
│   │   │   ├── search.py
│   │   │   └── categories.py
│   │   ├── /notifications
│   │   │   ├── __init__.py
│   │   │   ├── notification_manager.py
│   │   │   ├── realtime.py
│   │   │   ├── push_notifications.py
│   │   │   ├── email_notifications.py
│   │   │   └── preferences.py
│   │   └── /analytics
│   │       ├── __init__.py
│   │       ├── engagement_metrics.py
│   │       ├── reach_metrics.py
│   │       ├── audience_insights.py
│   │       └── performance_tracking.py
│   │
│   ├── /studio                  # 🎨 AI EDITOR SERVICE LAYER (NEW)
│   │   ├── __init__.py
│   │   ├── studio_service.py         # Main Service
│   │   ├── chat_engine.py            # Chat Processing
│   │   ├── content_generator.py      # Content Generation
│   │   ├── variant_manager.py        # Variant Management
│   │   ├── session_manager.py        # Session Persistence
│   │   ├── template_manager.py       # Template Management
│   │   └── analytics.py              # Studio Analytics
│   │
│   ├── /compliance              # ⚖️ COMPLIANCE LAYER (Extended)
│   │   ├── __init__.py
│   │   ├── /dsa
│   │   │   ├── /content_moderation
│   │   │   │   ├── __init__.py
│   │   │   │   ├── moderation_engine.py
│   │   │   │   ├── ai_moderator.py
│   │   │   │   ├── human_review.py
│   │   │   │   ├── priority_system.py
│   │   │   │   ├── automated_actions.py
│   │   │   │   ├── appeal_process.py
│   │   │   │   └── review_decisions.py
│   │   │   │
│   │   │   ├── /ai_detection
│   │   │   │   ├── __init__.py
│   │   │   │   ├── text_analyzer.py
│   │   │   │   ├── image_analyzer.py
│   │   │   │   ├── spam_detector.py
│   │   │   │   ├── bot_detector.py
│   │   │   │   ├── deepfake_detector.py
│   │   │   │   └── misinformation.py
│   │   │   │
│   │   │   ├── /reporting
│   │   │   │   ├── __init__.py
│   │   │   │   ├── report_handler.py
│   │   │   │   ├── report_categories.py
│   │   │   │   ├── evidence_collection.py
│   │   │   │   ├── reporter_protection.py
│   │   │   │   └── status_tracking.py
│   │   │   │
│   │   │   ├── /transparency
│   │   │   │   ├── __init__.py
│   │   │   │   ├── terms_of_service.py
│   │   │   │   ├── community_guidelines.py
│   │   │   │   ├── moderation_logs.py
│   │   │   │   ├── transparency_reports.py
│   │   │   │   ├── removal_reasons.py
│   │   │   │   └── statistics.py
│   │   │   │
│   │   │   ├── /algorithm_transparency
│   │   │   │   ├── __init__.py
│   │   │   │   ├── algorithm_disclosure.py
│   │   │   │   ├── parameters_explanation.py
│   │   │   │   ├── user_controls.py
│   │   │   │   ├── chronological_option.py
│   │   │   │   └── preference_settings.py
│   │   │   │
│   │   │   └── /crisis_response
│   │   │       ├── __init__.py
│   │   │       ├── crisis_detection.py
│   │   │       ├── emergency_response.py
│   │   │       └── coordination.py
│   │   │
│   │   ├── /gdpr              # ⭐ GDPR COMPLIANCE (Extended)
│   │   │   ├── __init__.py
│   │   │   ├── privacy_controls.py      # Privacy Settings Management
│   │   │   ├── consent_management.py    # Consent Tracking
│   │   │   ├── data_portability.py      # Data Export/Download
│   │   │   ├── right_to_erasure.py      # Complete Data Deletion
│   │   │   ├── cookie_consent.py        # Cookie Management
│   │   │   ├── audit_logs.py            # Audit Trail
│   │   │   └── dpia.py                  # Data Protection Impact Assessment
│   │   │
│   │   ├── /child_safety
│   │   │   ├── __init__.py
│   │   │   ├── age_verification.py      # Age Verification Logic
│   │   │   ├── parental_consent.py      # Parental Consent Management
│   │   │   ├── parental_controls.py     # Parental Control Features
│   │   │   ├── screen_time.py           # Screen Time Tracking
│   │   │   ├── content_restrictions.py  # Age-appropriate Content
│   │   │   ├── csam_detection.py        # CSAM Detection & Reporting
│   │   │   └── safety_settings.py       # Safety Feature Toggle
│   │   │
│   │   └── /drm
│   │       ├── __init__.py
│   │       ├── license_manager.py
│   │       ├── watermarking.py
│   │       ├── encryption.py
│   │       ├── access_control.py
│   │       └── audit.py
│   │
│   ├── /repositories            # 🗄️ REPOSITORY PATTERN (Data Access)
│   │   ├── __init__.py
│   │   ├── base_repository.py
│   │   ├── user_repository.py
│   │   ├── post_repository.py
│   │   ├── comment_repository.py
│   │   ├── like_repository.py
│   │   ├── follow_repository.py
│   │   ├── report_repository.py
│   │   ├── compliance_repository.py
│   │   ├── studio_repository.py      # (NEW)
│   │   └── notification_repository.py
│   │
│   ├── /websockets              # 🔌 WEBSOCKET SERVER
│   │   ├── __init__.py
│   │   ├── events.py             # Event Handlers
│   │   ├── social_socket.py       # Social Events
│   │   ├── notification_socket.py # Notifications
│   │   ├── live_room_socket.py    # LiveRoom Events
│   │   └── studio_socket.py       # (NEW) Studio Real-time Events
│   │
│   ├── /models                  # 📋 PYDANTIC MODELS
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── comment.py
│   │   ├── report.py
│   │   ├── studio.py             # (NEW)
│   │   ├── api_response.py        # Response Wrapper
│   │   └── errors.py             # Error Models (NEW)
│   │
│   ├── /middleware              # 🛡️ MIDDLEWARE
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── rate_limit.py
│   │   ├── error_handler.py      # (NEW)
│   │   ├── request_logging.py
│   │   └── feature_flag.py
│   │
│   ├── /utils                   # 🛠️ UTILITIES
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── cache.py
│   │   ├── validators.py
│   │   ├── decorators.py
│   │   └── constants.py
│   │
│   └── /celery_tasks            # 📦 BACKGROUND TASKS
│       ├── __init__.py
│       ├── ai_tasks.py
│       ├── moderation_tasks.py
│       ├── notification_tasks.py
│       ├── export_tasks.py
│       └── studio_tasks.py       # (NEW)
│
├── /tests
│   ├── test_auth.py
│   ├── test_social.py
│   ├── test_moderation.py
│   ├── test_compliance.py
│   ├── test_studio.py            # (NEW)
│   └── test_api.py
│
├── requirements.txt
├── config.py
└── wsgi.py
```

---

## 3. Neue API Endpoints v3.0

### ⭐ AI STUDIO Endpoints (NEW)

```python
# /api/v1/studio - User Studio APIs
POST   /api/v1/studio/chat              # Chat with Studio AI
       Request:  { message, project_id, context }
       Response: { response, suggestions, tokens_used }

GET    /api/v1/studio/projects          # List User Projects
       Response: { projects[], total, page }

POST   /api/v1/studio/projects          # Create Project
       Request:  { name, description, type }
       Response: { id, name, created_at }

GET    /api/v1/studio/projects/:id      # Get Project Details
       Response: { project, sessions, templates }

POST   /api/v1/studio/generate          # Generate Content
       Request:  { prompt, project_id, type, style }
       Response: { content, variants[], metadata }

POST   /api/v1/studio/variants          # Create Variant
       Request:  { content_id, style, parameters }
       Response: { variant_id, content, preview }

GET    /api/v1/studio/templates         # List Templates
       Response: { templates[], categories }

GET    /api/v1/studio/sessions/:id      # Get Session State
       Response: { session, messages, metadata }

GET    /api/v1/studio/history           # Studio History
       Request:  { page, limit, filter }
       Response: { items, total, has_more }

# /api/v1/admin-panel/studio - Admin Studio APIs
GET    /api/v1/admin-panel/studio/dashboard   # Studio Statistics
       Response: { active_users, total_generations, avg_tokens }

GET    /api/v1/admin-panel/studio/projects    # Manage Projects
       Response: { projects[], total }

PUT    /api/v1/admin-panel/studio/projects/:id # Update Project
       Request:  { status, featured, settings }
       Response: { success }

DELETE /api/v1/admin-panel/studio/projects/:id # Delete Project
       Response: { success }

GET    /api/v1/admin-panel/studio/templates   # Manage Templates
       Response: { templates[], total }

POST   /api/v1/admin-panel/studio/templates   # Create Template
       Request:  { name, content, category }
       Response: { id, name }
```

**WebSocket Events:**
```python
# Studio Events
'studio:message_received'      # { message, response, timestamp }
'studio:generation_started'    # { content_id, type }
'studio:generation_complete'   # { content_id, result }
'studio:variant_created'       # { variant_id, content }
'studio:session_updated'       # { session_id, state }
```

### ⭐ COMPLIANCE (GDPR) Endpoints (NEW)

```python
# /api/v1/compliance - User Compliance APIs
GET    /api/v1/compliance/privacy       # Get Privacy Settings
       Response: { user_id, privacy_level, data_usage, tracking }

PUT    /api/v1/compliance/privacy       # Update Privacy Settings
       Request:  { privacy_level, data_usage, tracking }
       Response: { success, updated_at }

GET    /api/v1/compliance/cookies       # Get Cookie Preferences
       Response: { essential, marketing, analytics, performance }

PUT    /api/v1/compliance/cookies       # Update Cookie Preferences
       Request:  { essential, marketing, analytics, performance }
       Response: { success, updated_at }

GET    /api/v1/compliance/consent       # Get All Consents
       Response: { consents[], updated_at }

GET    /api/v1/compliance/consent-history  # Consent History
       Request:  { page, limit }
       Response: { history[], total, page }

POST   /api/v1/compliance/data-export   # Request Data Export (GDPR Art. 20)
       Request:  { format: 'json' | 'csv' }
       Response: { request_id, status: 'processing', estimated_time }

GET    /api/v1/compliance/data-export/:request_id  # Get Export Status
       Response: { status, download_url, expires_at }

POST   /api/v1/compliance/data-deletion # Request Data Deletion (GDPR Art. 17)
       Request:  { reason, feedback }
       Response: { request_id, status: 'processing', deadline }

POST   /api/v1/compliance/parental-consent # Submit Parental Consent (COPPA)
       Request:  { parent_email, child_age, consent: true }
       Response: { success, verification_sent }
```

### ⭐ MODERATION SLA Monitor (NEW)

```python
GET    /api/v1/moderation/sla-monitor   # SLA Monitoring Dashboard
       Response: {
           total_reports: 150,
           by_priority: { critical: 5, high: 25, medium: 80, low: 40 },
           sla_compliance: 96.5,    # Percentage
           avg_response_time: 180,  # Minutes
           deadline_breaches: 5,
           overdue_reports: 2
       }
```

### ⭐ AUTH Age Verification (NEW)

```python
POST   /api/v1/auth/verify-age          # Verify Age (Child Safety)
       Request:  { age, method: 'dob' | 'parental_consent' }
       Response: { age_verified: true, expires_at }

GET    /api/v1/auth/age-verification-status # Check Status
       Response: { age_verified, age_verified_at, expires_at }
```

### ⭐ ADMIN Dashboard (NEW)

```python
GET    /api/v1/admin-panel/dashboard          # Admin Overview Dashboard
       Response: {
           active_users: 5000,
           total_posts: 45000,
           pending_reports: 25,
           moderation_queue_size: 15,
           system_health: {
               db_status: 'healthy',
               cache_status: 'healthy',
               worker_status: 'running'
           }
       }

GET    /api/v1/admin-panel/compliance         # Compliance Dashboard
       Response: {
           gdpr_requests_pending: 10,
           deletion_requests: 3,
           export_requests: 7,
           parental_consents_pending: 5,
           csam_reports: 2
       }
```

---

## 4. WebSocket Events - STANDARDIZED (NEW)

```python
# src/constants/events.constants.ts
WEBSOCKET_EVENTS = {
    # Auth
    'auth:login',
    'auth:logout',
    
    # Social - Posts
    'post:created',
    'post:updated',
    'post:deleted',
    'post:liked',
    'post:unliked',
    
    # Social - Comments
    'comment:created',
    'comment:deleted',
    'comment:liked',
    
    # Social - Follow
    'user:followed',
    'user:unfollowed',
    'user:online',
    'user:offline',
    
    # Notifications
    'notification:new',
    'notification:read',
    'notification:dismissed',
    
    # Messages
    'message:new',
    'message:read',
    'message:typing',
    
    # Moderation
    'moderation:action_taken',
    'report:status_changed',
    'appeal:status_changed',
    
    # Studio (NEW)
    'studio:message_received',
    'studio:generation_started',
    'studio:generation_complete',
    'studio:variant_created',
    'studio:session_updated',
    
    # LiveRoom
    'participant:joined',
    'participant:left',
    'whiteboard:updated',
    'recording:started',
    'recording:stopped',
    
    # Feed
    'feed:updated',
}

# Event Payload Schemas
{
    'post:created': {
        'post_id': 'str',
        'author_id': 'str',
        'title': 'str',
        'content': 'str',
        'timestamp': 'ISO8601'
    },
    
    'studio:generation_complete': {
        'content_id': 'str',
        'project_id': 'str',
        'result': 'str',
        'tokens_used': 'int',
        'timestamp': 'ISO8601'
    }
}
```

---

## 5. Error Response Format - STANDARDIZED (NEW)

### Success Response
```json
{
    "success": true,
    "data": {
        "id": "...",
        "name": "..."
    },
    "timestamp": "2026-01-13T10:30:00Z"
}
```

### Error Response
```json
{
    "success": false,
    "error": {
        "code": "AUTH_001",
        "message": "Invalid credentials",
        "details": "Email or password is incorrect",
        "field": "email"
    },
    "timestamp": "2026-01-13T10:30:00Z"
}
```

### Error Codes
```python
# Authentication Errors
AUTH_001 = "INVALID_CREDENTIALS"
AUTH_002 = "USER_NOT_FOUND"
AUTH_003 = "EMAIL_ALREADY_EXISTS"
AUTH_004 = "TOKEN_EXPIRED"
AUTH_005 = "INVALID_TOKEN"
AUTH_006 = "AGE_VERIFICATION_REQUIRED"

# Validation Errors
VAL_001 = "INVALID_INPUT"
VAL_002 = "REQUIRED_FIELD"
VAL_003 = "INVALID_FORMAT"

# Authorization Errors
PERM_001 = "UNAUTHORIZED"
PERM_002 = "FORBIDDEN"
PERM_003 = "INSUFFICIENT_PERMISSIONS"

# Resource Errors
RES_001 = "NOT_FOUND"
RES_002 = "CONFLICT"
RES_003 = "RESOURCE_LOCKED"

# Compliance Errors
COMP_001 = "AGE_VERIFICATION_FAILED"
COMP_002 = "PARENTAL_CONSENT_REQUIRED"
COMP_003 = "CONTENT_RESTRICTED_BY_POLICY"

# Feature Flag Errors
FEAT_001 = "FEATURE_NOT_AVAILABLE"
FEAT_002 = "FEATURE_DISABLED"

# Server Errors
SRV_001 = "INTERNAL_SERVER_ERROR"
SRV_002 = "SERVICE_UNAVAILABLE"
SRV_003 = "DATABASE_ERROR"
```

---

## 6. Feature Flag Names - STANDARDIZED (NEW)

```python
FEATURE_FLAGS = {
    # Social Network
    'user_posts',
    'feed_system',
    'follow_system',
    'likes_reactions',
    'comments',
    'content_sharing',
    'trending_discovery',
    'hashtags',
    'mentions',
    
    # Messaging
    'direct_messages',
    'group_chat',
    
    # AI Editor
    'ai_editor',
    'editor_chat',
    'editor_generation',
    'editor_templates',
    'editor_variants',
    
    # Compliance
    'gdpr_controls',
    'parental_controls',
    'age_verification',
    'cookie_consent',
    
    # Moderation
    'content_moderation',
    'user_reports',
    'appeal_process',
    'sla_monitoring',
    
    # Admin Features
    'admin_dashboard',
    'feature_flag_admin',
    'moderation_panel',
}
```

---

## 7. Authorization Decorators & RBAC 2.0 (Database-Driven)

### 🔐 Overview: Von Hardcoded zu Database-Driven

Das LSX Backend implementiert eine **RBAC 2.0 (Role-Based Access Control 2.0)** mit drei Decorators für Autorisierung:

| Decorator | Typ | Zweck | Permission Keys |
|-----------|-----|-------|-----------------|
| `@require_system_admin()` | Capability-Based | System-Level Admin Access | `admin:system` |
| `@require_org_admin()` | Capability-Based | Organization Admin Access | `manage:org:settings`, `admin:organisations` |
| `@require_org_member()` | Resource-Based | Organization Membership Check | Keine (direkter Organisationszugriff) |

**Wichtig:** RBAC 2.0 ist **database-driven** und ersetzt die deprecated hardcoded Role-Liste. Das ermöglicht dem **Role Studio Admin Panel**, Berechtigungen ohne Code-Änderungen zu aktualisieren!

---

### 📍 Decorator-Implementierung

#### 1. @require_system_admin()

**Zweck:** System-level administrative access control

**Implementierung:**
```python
@require_system_admin()
def admin_endpoint():
    """Requires system administrator role."""
    return jsonify({'data': 'admin-only'})
```

**Access-Kriterien (OR-Logik):**
- `hierarchy_level >= 9` (Emergency Fallback)
- User hat `admin:system` Permission in core.role_permissions

**Betroffene Roles:**
- `admin` (hierarchy_level: 9)
- `owner` (hierarchy_level: 11)

**Sicherheit:**
- Fail-Secure: Returns 403 Forbidden on database errors (NOT 500)
- SQL-Injection Prevention: Uses ParameterizedQueries
- Audit-Trail: All permission checks logged

---

#### 2. @require_org_admin()

**Zweck:** Organization-level administrative access (dual permission support)

**Implementierung:**
```python
@require_org_admin()
def org_admin_endpoint():
    """Requires organization admin role."""
    return jsonify({'data': 'org-admin-only'})
```

**Access-Kriterien (OR-Logik):**
- `hierarchy_level >= 5` (Emergency Fallback)
- User hat `manage:org:settings` Permission (organization management)
- User hat `admin:organisations` Permission (organization administration)

**Betroffene Roles:**
- `school_admin` (hierarchy_level: 5)
- `company_admin` (hierarchy_level: 6)
- `admin` (hierarchy_level: 9)
- `owner` (hierarchy_level: 11)

**Unterschied zu @require_system_admin:**
- Zwei Permission Keys (mehr Granularität)
- Niedrigere Hierarchy Level Thresholds
- Für Org-spezifische Admin-Tasks

---

#### 3. @require_org_member()

**Zweck:** RESOURCE-BASED access control (Organization Membership)

**Implementierung:**
```python
@require_org_member()
def org_scoped_endpoint(org_id):
    """Requires membership in specified organization."""
    return jsonify({'data': f'org-{org_id}-data'})
```

**Access-Kriterien:**
- System Admins (`hierarchy_level >= 9`) können auf beliebige Orgs zugreifen
- Regular Users müssen `org_id` Parameter mit ihrer `user.organisation_id` matchen

**Wichtig: Resource-Based vs. Capability-Based**
- `@require_system_admin()` & `@require_org_admin()`: **Capability-Based** (Was kann User TUN?)
- `@require_org_member()`: **Resource-Based** (Auf welche Organisationen kann User ZUGREIFEN?)

Diese architektonische Unterscheidung ist kritisch für korrekte Access Control!

---

### 🗄️ Database Schema: RBAC 2.0

**Drei kritische Tabellen:**

#### 1. core.permissions
```sql
-- Alle verfügbaren Permissions im System
CREATE TABLE core.permissions (
    permission_id SERIAL PRIMARY KEY,
    permission_key VARCHAR(100) UNIQUE NOT NULL,  -- e.g., 'admin:system'
    display_name VARCHAR(255),                     -- User-friendly name
    description TEXT,
    category VARCHAR(50),                          -- 'system', 'organization', etc.
    module VARCHAR(50),                            -- 'admin', 'organizations', etc.
    is_system BOOLEAN DEFAULT true,               -- System-managed?
    sort_order INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- RBAC 2.0 Permissions:
INSERT INTO core.permissions (permission_key, display_name, category, module) VALUES
    ('admin:system', 'System Administrator', 'system', 'admin'),           -- ID: 213
    ('manage:org:settings', 'Manage Organization Settings', 'organization', 'organizations'), -- ID: 214
    ('admin:organisations', 'Administer Organizations', 'organization', 'organizations');     -- ID: 215
```

#### 2. core.role_permissions
```sql
-- Junction table: Role → Permission Mappings
CREATE TABLE core.role_permissions (
    role_id INTEGER NOT NULL REFERENCES core.roles(role_id),
    permission_id INTEGER NOT NULL REFERENCES core.permissions(permission_id),
    PRIMARY KEY (role_id, permission_id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- RBAC 2.0 Mappings:
-- admin:system (213) → owner (11), admin (9)
INSERT INTO core.role_permissions (role_id, permission_id) VALUES
    (11, 213),  -- owner gets admin:system
    (9, 213);   -- admin gets admin:system

-- manage:org:settings (214) → owner, admin, company_admin, school_admin
INSERT INTO core.role_permissions (role_id, permission_id) VALUES
    (11, 214),  -- owner
    (9, 214),   -- admin
    (6, 214),   -- company_admin
    (5, 214);   -- school_admin

-- admin:organisations (215) → owner, admin, company_admin, school_admin
INSERT INTO core.role_permissions (role_id, permission_id) VALUES
    (11, 215),  -- owner
    (9, 215),   -- admin
    (6, 215),   -- company_admin
    (5, 215);   -- school_admin
```

#### 3. core.roles (Reference)
```sql
-- Roles with hierarchy levels
CREATE TABLE core.roles (
    role_id INTEGER PRIMARY KEY,
    role_name VARCHAR(100) NOT NULL,
    hierarchy_level INTEGER,  -- 0-11 (emergency fallback thresholds)
    created_at TIMESTAMP
);

-- Key Roles for RBAC 2.0:
-- (5, 'school_admin', 5)      -- hierarchy_level >= 5
-- (6, 'company_admin', 6)     -- hierarchy_level >= 5
-- (9, 'admin', 9)             -- hierarchy_level >= 9
-- (11, 'owner', 11)           -- hierarchy_level >= 9
```

---

### 🔄 Permission Check Flow

```
User Request to Protected Endpoint
  ↓
Decorator Interceptor (@require_system_admin)
  ↓
Has Permission in Database?
  ├─ Query: core.role_permissions WHERE role_id = ? AND permission_id = ?
  │  (Uses PermissionRepository.user_has_permission)
  │  ↓
  │  Permission Found? → ✅ ALLOW (HTTP 200+)
  │  Permission Not Found? → Check Fallback
  │
  └─ Fallback: hierarchy_level >= 9?
     ├─ YES → ✅ ALLOW (Backward Compatible)
     └─ NO → ❌ DENY (HTTP 403 Forbidden)

Database Error? → ❌ DENY (HTTP 403 Forbidden - Fail-Secure Design)
```

---

### 💡 Backward Compatibility & Emergency Fallback

**Design Decision:** Alle drei Decorators behalten `hierarchy_level` Checks:

```python
# @require_system_admin Flow:
1. Check Database: PermissionRepository.user_has_permission('admin:system')
2. If DB Check = TRUE: Grant Access ✅
3. If DB Check = FALSE: Check Fallback hierarchy_level >= 9
4. If Fallback = TRUE: Grant Access ✅ (Emergency Access)
5. Otherwise: Deny Access ❌

# Benefit:
- Wenn PermissionRepository fehlschlägt: Keine Requests sind blockiert
- Hierarchy Level bietet Safety Net für emergencies
- Fail-Secure: Fehler = Deny (nicht Allow!)
```

---

### 📊 Permission Status

| Permission | Permission ID | Roles | Hierarchy Levels | Status |
|-----------|--------------|-------|-----------------|--------|
| `admin:system` | 213 | owner (11), admin (9) | 10, 9 | ✅ Active |
| `manage:org:settings` | 214 | owner, admin, company_admin, school_admin | 10, 9, 6, 5 | ✅ Active |
| `admin:organisations` | 215 | owner, admin, company_admin, school_admin | 10, 9, 6, 5 | ✅ Active |

**Total Mappings:** 10 role-permission relationships in core.role_permissions

---

### 🔒 Security Guarantees

| Aspect | Implementation |
|--------|-----------------|
| **SQL Injection Prevention** | Parameterized Queries in PermissionRepository |
| **Access Control** | Database-Driven (not hardcoded) |
| **Fail-Secure** | Returns 403 on database errors (not 500) |
| **Audit Trail** | All permission checks logged via middleware |
| **Backward Compat** | hierarchy_level fallback for emergency access |

---

### 📖 Detaillierte Dokumentation

Für vollständige Details siehe:
- **Sicherheit & Architektur:** [`01_Core/05_Sicherheit-Berechtigungen.md`](./05_Sicherheit-Berechtigungen.md) - Section 6.1 RBAC 2.0
- **Implementierung:** `backend/app/security/permissions.py` (455 lines, Quality Gate G01-G10 passed)
- **Tests:** `backend/tests/unit/test_permission_decorators.py` (15+ test cases)
- **Migrations:**
  - `backend/migrations/01_Core/080_add_rbac2_permissions.sql`
  - `backend/migrations/01_Core/081_map_rbac2_permissions_to_roles.sql`

---

## 8. Zusammenfassung v3.0

### ✅ Neue Features

| Feature | Status | APIs | WebSocket Events |
|---------|--------|------|------------------|
| **AI Editor** | ✅ | 8 Endpoints | 5 Events |
| **Compliance (GDPR)** | ✅ | 9 Endpoints | — |
| **Age Verification** | ✅ | 2 Endpoints | — |
| **SLA Monitor** | ✅ | 1 Endpoint | — |
| **Admin Dashboard** | ✅ | 2 Endpoints | — |
| **Error Standardization** | ✅ | All Endpoints | — |
| **WebSocket Standardization** | ✅ | — | 25 Events |

### 💡 Backend Architecture v3.0

```
┌──────────────────────────────────────────────────────────────┐
│  🎯 Enterprise-Grade Social Learning Platform v3.0           │
│  ───────────────────────────────────────────────────────────  │
│                                                               │
│  ✅ Feature Flag System (Progressive Rollout)                │
│  ✅ Social Network (Posts, Feed, Follow, Engagement)         │
│  ✅ AI Editor (Chat, Generate, Variants, Templates)          │
│  ✅ Full Compliance (DSA/NetzDG/GDPR/ISO 27001/Child)        │
│  ✅ Content Moderation (AI + Human, 24h/7d SLA)              │
│  ✅ GDPR APIs (Data Export, Deletion, Privacy)               │
│  ✅ Age Verification & Parental Controls                     │
│  ✅ WebSocket Events (Standardized)                          │
│  ✅ Error Format (Standardized)                              │
│  ✅ DRM System (Denuvo-style Protection)                     │
│  ✅ Trust & Safety (Monitoring & Analytics)                  │
│  ✅ Internationalization (20+ Languages)                     │
│                                                               │
│  🐍 Python 3.12+ | 🌶️ Flask 3.0 | 🐘 PostgreSQL            │
│  🔴 Redis | 📦 Celery | 🔑 JWT | 📋 Pydantic              │
│  🎨 AI Editor | 🛡️ Compliance | 📡 WebSockets             │
│  🗄️ psycopg3 + Repository Pattern (KEIN ORM!)               │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## 9. Admin Panel Reorganization v3.1 (16.01.2026)

### 🔄 Architektur-Änderung: Settings-Based Structure

**Ziel:** Backend-Struktur an Frontend Sidebar ausrichten für bessere Wartbarkeit.

### Vorher (v3.0):

```
/admin/
├── /ai/                 # 14 AI-related endpoints
├── /courses/            # Course management
├── /studio/             # AI Editor admin
├── /moderation/         # Moderation panel
├── /feature_flags/      # Feature flags
└── system.py            # System settings (scattered)
```

**Problem:**
- Struktur nicht aligned mit Frontend Sidebar
- Settings verstreut (AI, System, Permissions getrennt)
- Schwer zu navigieren

### Nachher (v3.1):

```
/admin/
├── /settings/           # ⚙️ ALLE Settings konsolidiert
│   ├── /ai/             # 14 AI configuration endpoints
│   ├── /system/         # System settings & monitoring
│   ├── /permissions/    # Roles & permission thresholds
│   └── /feature_flags/  # Feature flag management
│
├── /audit_logs/         # 📋 Top-Level (eigenes Sidebar-Item)
├── /courses/            # 📚 Top-Level (eigenes Sidebar-Item)
├── /moderation/         # 🛡️ Top-Level (eigenes Sidebar-Item)
└── [other top-level items...]
```

**Vorteile:**
✅ Frontend Sidebar spiegelt Backend-Struktur 1:1
✅ Alle Settings unter einem Dach (`/settings/`)
✅ Bessere Organisation & Wartbarkeit
✅ Einfachere Navigation für Entwickler

### Route-Änderungen:

| Alt (v3.0) | Neu (v3.1) | Status |
|-----------|-----------|--------|
| `/api/v1/admin-panel/ai/*` | `/api/v1/admin-panel/settings/ai/*` | ✅ Migrated (14 endpoints) |
| `/api/v1/admin-panel/system/*` | `/api/v1/admin-panel/settings/system/*` | ✅ Migrated (3 endpoints) |
| `/api/v1/admin-panel/roles` | `/api/v1/admin-panel/settings/permissions/roles` | ✅ Migrated |
| `/api/v1/admin-panel/permissions` | `/api/v1/admin-panel/settings/permissions` | ✅ Migrated |

**Keine Breaking Changes:**
- Alle Blueprint `url_prefix` aktualisiert
- Alle Imports aktualisiert
- Backend startet fehlerfrei
- Alle 50+ Routes funktionieren

**Dateien betroffen:** 20 Files moved/updated (AI settings, system settings, permissions)

**Migrations:** Keine DB-Änderungen nötig (nur Route-Pfade)

---

## 10. Semantic URL Paths v3.2 (16.01.2026)

### 🎯 URL-Umbenennung: `/admin/` → `/admin-panel/`

**Ziel:** Semantische Klarheit in API-Endpunkten - Unterscheidung zwischen "Admin Role" und "Admin Panel Interface".

### Rationale:

**Problem mit `/admin/`:**
- ❓ Mehrdeutig: Bezieht sich auf Admin-Rolle oder Admin-Panel-Interface?
- ❓ Könnte auch Admin-User-Management bedeuten
- ❓ Nicht selbsterklärend für neue Entwickler

**Lösung mit `/admin-panel/`:**
- ✅ **EINDEUTIG**: Bezieht sich explizit auf Admin Panel Interface
- ✅ **SELBSTERKLÄREND**: Jeder weiß sofort was gemeint ist
- ✅ **SEMANTIC**: URL beschreibt WAS, nicht WER

### Route-Änderungen v3.2:

| Alt (v3.1) | Neu (v3.2) | Typ |
|-----------|-----------|-----|
| `/api/v1/admin/settings/ai/*` | `/api/v1/admin-panel/settings/ai/*` | Admin Panel Settings |
| `/api/v1/admin/courses/*` | `/api/v1/admin-panel/courses/*` | Admin Panel Course Mgmt |
| `/api/v1/admin/moderation/*` | `/api/v1/admin-panel/moderation/*` | Admin Panel Moderation |
| `/api/v1/admin/analytics` | `/api/v1/admin-panel/analytics` | Admin Panel Analytics |
| `/api/v1/admin/tutor` | `/api/v1/admin-panel/tutor` | Admin Panel Tutor Config |
| `/api/admin/i18n-sync` | `/api/admin-panel/i18n-sync` | Admin Panel i18n |
| `/dashboard/admin/system` | `/dashboard/admin-panel/system` | Admin Panel Dashboard |

### Implementation:

**Betroffene Dateien:** 24 Blueprint-Dateien

**Änderungen:**
- ✅ Alle `url_prefix='/admin/...'` → `url_prefix='/admin-panel/...'`
- ✅ Settings: 14 AI endpoints
- ✅ Settings: 3 System endpoints
- ✅ Settings: 2 Permission endpoints
- ✅ Courses: 6 endpoints
- ✅ Moderation: 5 endpoints
- ✅ Other: Analytics, Tutor, i18n, Dashboard

**Keine Breaking Changes:**
- ✅ System noch in Entwicklung (nicht produktiv)
- ✅ Frontend kann parallel angepasst werden
- ✅ Keine DB-Änderungen nötig
- ✅ Alle Blueprint-Registrierungen funktionieren

**Vorteile:**
- 🎯 **Semantische Klarheit**: "admin-panel" = Interface, "admin" = Rolle
- 📖 **Bessere Dokumentation**: Self-documenting URLs
- 🚀 **Zukunftssicher**: Klare Trennung für spätere Features
- 🔍 **Leichter zu debuggen**: Logs zeigen explizit "admin-panel"

### Code-Struktur:

**WICHTIG:** Der Ordnername im Code bleibt `/admin/`!

```
backend/app/api/v1/
└── admin/              # ← Ordnername bleibt!
    ├── settings/
    │   └── ai/
    │       └── jobs.py
    │           url_prefix='/admin-panel/settings/ai/jobs'  # ← URL geändert!
```

**Grund:** Ordnername = Technische Organisation, URL = Semantische API-Interface

---

## 📌 Dokument abgeschlossen

**Version:** 3.2
**Status:** Final
**Letzte Aktualisierung:** 16.01.2026

**Neue Features v3.0:**
- ✅ Complete AI Editor Integration (8 APIs + 5 WebSocket Events)
- ✅ GDPR Compliance APIs (9 Endpoints)
- ✅ Age Verification & Parental Controls
- ✅ SLA Monitoring for Moderation
- ✅ Admin Dashboard APIs
- ✅ Standardized Error Response Format (20+ Error Codes)
- ✅ Standardized WebSocket Events (25+ Events)
- ✅ Standardized Feature Flag Names
- ✅ Compliance Dashboard APIs
- ✅ Complete AI Editor Service Layer

> **WICHTIG:** 
> - Backend und Frontend sind jetzt **100% abgestimmt**
> - Feature Flags consistent benannt
> - WebSocket Events standardisiert
> - Error Format standardisiert
> - AI Editor vollständig integriert
> - GDPR compliant
