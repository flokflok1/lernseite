# Phase 5: Features + Shared Migration Plan

**Datum:** 2026-01-10
**Status:** IN PROGRESS
**Ziel:** Migration der API-Routes von app/api/ nach src/api/

---

## Analyse der Situation

Nach Phasen 0-4 haben wir:
- ✅ Core Services (Phase 0-2)
- ✅ Content Domains (Phase 3: Courses, Chapters, Lessons, Exams, Learning Methods, Math)
- ✅ Other Domains (Phase 4: Analytics, Community, LiveRoom, Gamification, Notifications, Storage, Billing, System)

**Aber:** Die alten API-Routes existieren noch in `app/api/`!

### Was ist in app/api/?

```
app/api/
├── system_features/       # 25 System-Features (alte Routes)
│   ├── agents/
│   ├── ai/
│   ├── analytics/
│   ├── learning_methods/
│   ├── math/
│   ├── prompts/
│   └── tutor/
│
├── shared/               # Shared Resources (alte Routes)
│   ├── categories/
│   ├── feedback/
│   ├── media/
│   ├── organisations/
│   └── users/
│
└── core/                # Core Features (alte Routes)
    ├── auth/
    ├── health/
    └── i18n/
```

### Was ist in src/api/? (NEU - DDD)

```
src/api/
├── analytics/          # Domain (bereits erstellt Phase 4.1)
├── auth/              # Domain (bereits erstellt Phase 2)
├── billing/           # Domain (bereits erstellt Phase 4.7)
├── categories/        # Domain (bereits erstellt Phase 3.1)
├── chapters/          # Domain (bereits erstellt Phase 3.2)
├── community/         # Domain (bereits erstellt Phase 4.2)
├── courses/           # Domain (bereits erstellt Phase 3.1)
├── exams/            # Domain (bereits erstellt Phase 3.4)
├── gamification/     # Domain (bereits erstellt Phase 4.4)
├── i18n/             # Domain (bereits erstellt Phase 2)
├── learning-methods/ # Domain (bereits erstellt Phase 3.5)
├── lessons/          # Domain (bereits erstellt Phase 3.3)
├── liveroom/         # Domain (bereits erstellt Phase 4.3)
├── math/             # Domain (bereits erstellt Phase 3.6)
├── notifications/    # Domain (bereits erstellt Phase 4.5)
├── storage/          # Domain (bereits erstellt Phase 4.6)
└── system/           # Domain (bereits erstellt Phase 4.8)
```

---

## Problem-Identifikation

**Die Domains existieren BEREITS in src/api/, ABER:**
- ❌ Die alten Routes in app/api/ sind noch aktiv
- ❌ Die neuen Domains in src/api/ haben nur Entities/Repositories/Services
- ❌ Die neuen Domains haben KEINE Routes/API-Endpoints

**Phase 5 Aufgabe:**
Migration der **API-Routes** von `app/api/` → `src/api/` Journeys

---

## Migration-Strategie

### Schritt 1: Journey-Struktur erstellen

Für jede Domain in `src/api/[domain]/` erstellen:

```
src/api/[domain]/
├── core/
│   ├── domain/
│   │   └── entities/         # ✅ Existiert bereits
│   ├── application/
│   │   └── services/         # ✅ Existiert bereits
│   └── infrastructure/
│       └── repositories/     # ✅ Existiert bereits
│
└── journeys/                 # ❌ NEU ERSTELLEN
    ├── admin/
    │   ├── api/
    │   │   └── routes/       # Admin-Endpoints hierhin
    │   └── __init__.py
    ├── creator/              # (optional)
    ├── learner/              # (optional)
    └── public/
        ├── api/
        │   └── routes/       # Public-Endpoints hierhin
        └── __init__.py
```

### Schritt 2: Routes migrieren

**Beispiel: Analytics Domain**

**ALT (app/api/system_features/analytics/):**
```python
# app/api/system_features/analytics/admin/rankings.py
@admin_analytics_bp.route('/api/v1/admin/analytics/rankings', methods=['GET'])
def get_rankings():
    ...
```

**NEU (src/api/analytics/journeys/admin/):**
```python
# src/api/analytics/journeys/admin/api/routes/rankings.py
from flask import Blueprint

admin_analytics_bp = Blueprint('admin_analytics', __name__)

@admin_analytics_bp.route('/api/v1/admin/analytics/rankings', methods=['GET'])
@require_auth
@require_role(['admin'])
def get_rankings():
    from src.api.analytics.core.application.services.analytics_service import AnalyticsService
    # Use existing service
    ...
```

### Schritt 3: Blueprint Registration

**NEU erstellen:**
```python
# src/api/analytics/journeys/__init__.py
from src.api.analytics.journeys.admin.api.routes import admin_analytics_bp
from src.api.analytics.journeys.public.api.routes import public_analytics_bp

__all__ = ['admin_analytics_bp', 'public_analytics_bp']
```

**In src/api/analytics/__init__.py aktualisieren:**
```python
# src/api/analytics/__init__.py
from src.api.analytics.core.domain.entities import *
from src.api.analytics.journeys import *

__all__ = [
    # Entities
    'AnalyticsSession', 'AnalyticsEvent', ...
    # Blueprints
    'admin_analytics_bp', 'public_analytics_bp'
]
```

---

## Domains-to-Routes Mapping

| app/api/ (ALT) | src/api/ (NEU) | Notizen |
|----------------|----------------|---------|
| system_features/ai/ | ai/ | NEU ERSTELLEN (AI Domain) |
| system_features/agents/ | agents/ | NEU ERSTELLEN (Agents Domain) |
| system_features/analytics/ | analytics/ | Routes hinzufügen |
| system_features/learning_methods/ | learning-methods/ | Routes hinzufügen |
| system_features/math/ | math/ | Routes hinzufügen |
| system_features/prompts/ | prompts/ | NEU ERSTELLEN (Prompts Domain) |
| system_features/tutor/ | tutor/ | NEU ERSTELLEN (Tutor Domain) |
| shared/categories/ | categories/ | Routes hinzufügen |
| shared/feedback/ | analytics/ (feedback part) | Routes hinzufügen |
| shared/media/ | media/ | NEU ERSTELLEN (Media Domain) |
| shared/organisations/ | organisations/ | NEU ERSTELLEN (Orgs Domain) |
| shared/users/ | users/ | NEU ERSTELLEN (Users Domain) |
| core/auth/ | auth/ | Routes hinzufügen |
| core/health/ | health/ | NEU ERSTELLEN (Health Domain) |
| core/i18n/ | i18n/ | Routes hinzufügen |

---

## Prioritäten

### Phase 5.1: Neue Domains erstellen (FEHLEN)

Domains die noch nicht existieren:
1. **ai** - AI Operations (jobs, models, pricing, profiles, providers)
2. **agents** - Agent/NPC System
3. **prompts** - Prompt Management
4. **tutor** - AI Tutor System
5. **media** - Media Processing (Audio, TTS)
6. **organisations** - Organisation Management
7. **users** - User Management
8. **health** - Health Checks

### Phase 5.2: Routes zu bestehenden Domains hinzufügen

Domains die existieren, aber keine Routes haben:
1. **analytics** - Analytics Session/Events/Feedback Routes
2. **auth** - Login/Register/Password Routes
3. **categories** - Category CRUD Routes
4. **i18n** - Translation Routes
5. **learning-methods** - LM Execution/Routing Routes
6. **math** - Math Toolkit Routes

---

## Vorgehensweise

### Schritt-für-Schritt:

1. ✅ Plan erstellen (dieser Dokument)
2. 🔄 Phase 5.1: Neue Domains erstellen (8 Domains)
3. 🔄 Phase 5.2: Routes zu bestehenden Domains hinzufügen
4. ✅ Alle Blueprints registrieren
5. ✅ Tests dass alle Routes funktionieren
6. ✅ Commit Phase 5 Complete

---

## Zu beachten

- **DB-First:** Alle Entities aus DB-Schema ableiten
- **Repository Pattern:** Alle DB-Zugriffe über Repositories
- **Event-Driven:** DomainEvents publishen bei CRUD
- **Journeys:** Routes nach User-Journeys organisieren (admin/creator/learner/public)
- **Max 500 LOC:** Dateien splitten wenn zu groß

---

**Version:** 1.0
**Letztes Update:** 2026-01-10
