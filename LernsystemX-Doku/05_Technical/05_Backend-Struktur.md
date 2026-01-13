# 17 – Backend-Struktur (Final) v3.0

**Version:** 3.0  
**Stand:** 13.01.2026  
**Änderungen:** Complete Enterprise Architecture + AI Studio APIs + Compliance GDPR APIs + Error/WebSocket Standardisierung

---

## Überblick

Dieses Dokument beschreibt die komplette **Enterprise-Grade Backend-Architektur** des LSX Lernsystems.

Das Backend ist **modular**, **sicher**, **skalierbar**, **vollständig compliance-konform**, **feature-flag-gesteuert** und **mit AI Studio integriert**.

### 🎯 Neue Features in v3.0

- ✅ **AI Studio System** - Chat, Content Generation, Variants, Sessions
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
        STUDIO[🎨 AI Studio<br/>Content Generation]

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
│   │   │   ├── exam_simulations.py
│   │   │   │
│   │   │   ├── # KI/Tutor API
│   │   │   ├── tutor.py
│   │   │   ├── agents.py
│   │   │   ├── audio.py
│   │   │   ├── tts.py
│   │   │   ├── math_toolkit.py
│   │   │   │
│   │   │   ├── # Analytics API
│   │   │   ├── analytics.py
│   │   │   ├── org_analytics.py
│   │   │   ├── feedback.py
│   │   │   │
│   │   │   ├── /social          # 🌟 SOCIAL API (Feature-Flagged)
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
│   │   │   ├── /compliance      # ⭐ GDPR COMPLIANCE APIs (NEW)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── privacy.py           # GET/PUT /api/v1/compliance/privacy
│   │   │   │   ├── cookies.py           # GET/PUT /api/v1/compliance/cookies
│   │   │   │   ├── consent.py           # GET /api/v1/compliance/consent
│   │   │   │   ├── data_export.py       # POST /api/v1/compliance/data-export
│   │   │   │   ├── data_deletion.py     # POST /api/v1/compliance/data-deletion
│   │   │   │   ├── consent_history.py   # GET /api/v1/compliance/consent-history
│   │   │   │   └── parental_consent.py  # POST /api/v1/compliance/parental-consent
│   │   │   │
│   │   │   ├── /moderation      # 🛡️ MODERATION APIs
│   │   │   │   ├── __init__.py
│   │   │   │   ├── reports.py           # POST /api/v1/moderation/reports
│   │   │   │   ├── queue.py             # GET /api/v1/moderation/queue
│   │   │   │   ├── actions.py           # POST /api/v1/moderation/actions
│   │   │   │   ├── statistics.py        # GET /api/v1/moderation/statistics
│   │   │   │   ├── sla_monitor.py       # GET /api/v1/moderation/sla-monitor (NEW)
│   │   │   │   └── appeals.py           # GET /api/v1/moderation/appeals
│   │   │   │
│   │   │   ├── /admin           # 👑 ADMIN API
│   │   │   │   ├── __init__.py
│   │   │   │   │
│   │   │   │   ├── /courses
│   │   │   │   │   ├── courses.py
│   │   │   │   │   ├── chapters.py
│   │   │   │   │   ├── lessons.py
│   │   │   │   │   ├── exams.py
│   │   │   │   │   ├── course_prompts.py
│   │   │   │   │   └── course_files.py
│   │   │   │   │
│   │   │   │   ├── /ai
│   │   │   │   │   ├── ai_jobs.py
│   │   │   │   │   ├── ai_models.py
│   │   │   │   │   ├── ai_model_profiles.py
│   │   │   │   │   ├── ai_tutor.py
│   │   │   │   │   └── ai_authoring.py
│   │   │   │   │
│   │   │   │   ├── /studio      # ⭐ AI STUDIO ADMIN APIs (NEW)
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── studio.py                 # GET /api/v1/admin/studio
│   │   │   │   │   ├── studio_projects.py        # Studio Projects CRUD
│   │   │   │   │   ├── studio_sessions.py        # Session Management
│   │   │   │   │   ├── studio_templates.py       # Template Management
│   │   │   │   │   └── studio_variants.py        # Variant Management
│   │   │   │   │
│   │   │   │   ├── /moderation
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── queue.py
│   │   │   │   │   ├── actions.py
│   │   │   │   │   ├── reports.py
│   │   │   │   │   ├── statistics.py
│   │   │   │   │   └── transparency.py
│   │   │   │   │
│   │   │   │   ├── /feature_flags
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── flags.py
│   │   │   │   │   ├── rollout.py
│   │   │   │   │   └── analytics.py
│   │   │   │   │
│   │   │   │   ├── dashboard.py         # GET /api/v1/admin/dashboard (NEW)
│   │   │   │   ├── users.py
│   │   │   │   ├── analytics.py
│   │   │   │   ├── system.py
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
│   │   └── /studio              # ⭐ AI STUDIO API (NEW)
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
│   ├── /studio                  # 🎨 AI STUDIO SERVICE LAYER (NEW)
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

# /api/v1/admin/studio - Admin Studio APIs
GET    /api/v1/admin/studio/dashboard   # Studio Statistics
       Response: { active_users, total_generations, avg_tokens }

GET    /api/v1/admin/studio/projects    # Manage Projects
       Response: { projects[], total }

PUT    /api/v1/admin/studio/projects/:id # Update Project
       Request:  { status, featured, settings }
       Response: { success }

DELETE /api/v1/admin/studio/projects/:id # Delete Project
       Response: { success }

GET    /api/v1/admin/studio/templates   # Manage Templates
       Response: { templates[], total }

POST   /api/v1/admin/studio/templates   # Create Template
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
GET    /api/v1/admin/dashboard          # Admin Overview Dashboard
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

GET    /api/v1/admin/compliance         # Compliance Dashboard
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
    
    # AI Studio
    'ai_studio',
    'studio_chat',
    'studio_generation',
    'studio_templates',
    'studio_variants',
    
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

## 7. Zusammenfassung v3.0

### ✅ Neue Features

| Feature | Status | APIs | WebSocket Events |
|---------|--------|------|------------------|
| **AI Studio** | ✅ | 8 Endpoints | 5 Events |
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
│  ✅ AI Studio (Chat, Generate, Variants, Templates)          │
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
│  🎨 AI Studio | 🛡️ Compliance | 📡 WebSockets             │
│  🗄️ psycopg3 + Repository Pattern (KEIN ORM!)               │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## 📌 Dokument abgeschlossen

**Version:** 3.0  
**Status:** Final  
**Letzte Aktualisierung:** 13.01.2026

**Neue Features v3.0:**
- ✅ Complete AI Studio Integration (8 APIs + 5 WebSocket Events)
- ✅ GDPR Compliance APIs (9 Endpoints)
- ✅ Age Verification & Parental Controls
- ✅ SLA Monitoring for Moderation
- ✅ Admin Dashboard APIs
- ✅ Standardized Error Response Format (20+ Error Codes)
- ✅ Standardized WebSocket Events (25+ Events)
- ✅ Standardized Feature Flag Names
- ✅ Compliance Dashboard APIs
- ✅ Complete Studio Service Layer

> **WICHTIG:** 
> - Backend und Frontend sind jetzt **100% abgestimmt**
> - Feature Flags consistent benannt
> - WebSocket Events standardisiert
> - Error Format standardisiert
> - AI Studio vollständig integriert
> - GDPR compliant
