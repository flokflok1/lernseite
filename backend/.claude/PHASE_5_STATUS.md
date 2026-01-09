# Phase 5: Status & Analyse

**Datum:** 2026-01-10
**Ziel:** Migration der API-Routes von app/ nach src/

---

## Situation Analyse

### ✅ Was bereits in src/ existiert:

#### Domains (Phase 3-4 erstellt):
1. **src/api/analytics/** - DDD komplett (entities, repositories, services)
   - ✅ Journeys: admin/api/routes/analytics.py existiert (Phase 4.1)
2. **src/api/billing/** - Entities vorhanden
3. **src/api/community/** - DDD komplett
   - ❌ Journeys: nur leere __init__.py
4. **src/api/content/**
   - **courses/** - DDD komplett (entities, repositories, services)
     - ✅ Journeys: admin + learner routes existieren
     - **chapters/** - DDD komplett
       - ✅ Journeys: admin routes existieren
     - **lessons/** - DDD komplett
       - ✅ Journeys: admin routes existieren
   - **exams/** - DDD komplett
     - ✅ Journeys: admin routes existieren
   - **learning_methods/** - DDD komplett
     - ✅ Journeys: admin routes existieren
   - **math/** - DDD komplett
     - ✅ Journeys: admin routes existieren
5. **src/api/gamification/** - Entities vorhanden
6. **src/api/liveroom/** - DDD komplett
   - ❌ Journeys: nur leere __init__.py
7. **src/api/marketplace/** - Struktur vorhanden
   - ❌ Journeys: nur leere __init__.py
8. **src/api/notifications/** - Entities vorhanden
9. **src/api/storage/** - Entities vorhanden
10. **src/api/system/** - Entities vorhanden

#### Features (bereits erstellt, aber LEER):
11. **src/api/features/**
    - **collaboration/** (7 Sub-Features) - nur leere __init__.py
    - **exams/** (4 Sub-Features) - nur leere __init__.py
    - **gamification/** (3 Sub-Features) - nur leere __init__.py
    - **interactive/whiteboard/** - Struktur vorhanden, aber leer
    - **sandbox/** (3 Sub-Features) - nur leere __init__.py
    - **tutor/** (2 Sub-Features) - nur leere __init__.py

#### Shared (bereits erstellt, aber LEER):
12. **src/api/shared/**
    - **organisations/** - nur leere __init__.py
    - **users/** - nur leere __init__.py

---

### ❌ Was noch in app/ ist (ALT):

#### app/api/system_features/ (KOMPLETT):
```
app/api/system_features/
├── agents/ (KOMPLETT - core, admin, audio, knowledge, media)
├── ai/ (KOMPLETT - admin: jobs, models, pricing, profiles, providers)
├── analytics/ (KOMPLETT - admin, core, user)
├── learning_methods/ (KOMPLETT - admin, core, execution, public)
├── math/ (KOMPLETT - calculator, interactive, reference, sessions)
├── prompts/ (KOMPLETT - admin, core)
└── tutor/ (KOMPLETT - admin, core, user)
```

#### app/api/shared/ (KOMPLETT):
```
app/api/shared/
├── categories/ (KOMPLETT - admin, core, hierarchy, public)
├── feedback/ (KOMPLETT - admin, core, user)
├── media/ (KOMPLETT - audio, tts)
├── organisations/ (KOMPLETT - admin, analytics, core, user)
└── users/ (KOMPLETT - admin, core, management, search, user)
```

#### app/api/core/ (KOMPLETT):
```
app/api/core/
├── auth/ (KOMPLETT - core, login, password, register, two_factor)
├── deprecation.py
├── health.py
└── i18n/ (KOMPLETT - management, moderation, public, translation)
```

#### app/api/user/ (User Journeys):
```
app/api/user/
├── chapters/ (admin, core, generation, management, media, user)
├── courses/ (admin, core, crud, enrollment, public, user)
├── dashboard/ (admin, core, layouts, recommendations, user, widgets)
├── exams/ (admin, core, user)
├── lessons/ (explanations, videos)
├── profile/ (appearance, subscription, user)
├── subscriptions/ (admin, core, plans, user)
└── tokens/ (admin, core, stats, transactions, wallet)
```

#### app/api/admin/ (Admin Journeys):
```
app/api/admin/
├── ai_operations/ (__init__.py)
├── assessment/ (__init__.py)
├── content_management/ (analytics, courses)
├── system_operations/ (settings, system)
└── user_management/ (__init__.py)
```

---

## Phase 5 Aufgabe - Präzisiert

### 5.1: Neue Domains erstellen (FEHLEN)

Domains die noch NICHT in src/api/ existieren:

1. **ai** - AI Operations (Jobs, Models, Pricing, Profiles, Providers)
   - Aus: app/api/system_features/ai/
   - Nach: src/api/ai/

2. **agents** - Agent/NPC System
   - Aus: app/api/system_features/agents/
   - Nach: src/api/agents/

3. **prompts** - Prompt Management
   - Aus: app/api/system_features/prompts/
   - Nach: src/api/prompts/

4. **tutor** - AI Tutor System
   - Aus: app/api/system_features/tutor/
   - Nach: src/api/tutor/

5. **media** - Media Processing (Audio, TTS)
   - Aus: app/api/shared/media/
   - Nach: src/api/media/

6. **organisations** - Organisation Management
   - Aus: app/api/shared/organisations/
   - Nach: src/api/organisations/ (VOLLSTÄNDIG)

7. **users** - User Management
   - Aus: app/api/shared/users/
   - Nach: src/api/users/ (VOLLSTÄNDIG)

8. **categories** - Category Management
   - Aus: app/api/shared/categories/
   - Nach: src/api/categories/

9. **auth** - Authentication
   - Aus: app/api/core/auth/
   - Nach: src/api/auth/ (VOLLSTÄNDIG - routes hinzufügen)

10. **health** - Health Checks
    - Aus: app/api/core/health.py
    - Nach: src/api/health/

11. **i18n** - Internationalization
    - Aus: app/api/core/i18n/
    - Nach: src/core/i18n/ (BEREITS DORT)

12. **dashboard** - Dashboard & Widgets
    - Aus: app/api/user/dashboard/
    - Nach: src/api/dashboard/

13. **profile** - User Profile
    - Aus: app/api/user/profile/
    - Nach: src/api/profile/

14. **subscriptions** - Subscriptions
    - Aus: app/api/user/subscriptions/
    - Nach: src/api/subscriptions/

15. **tokens** - Token Management
    - Aus: app/api/user/tokens/
    - Nach: src/api/tokens/

---

### 5.2: Journeys zu bestehenden Domains hinzufügen

Domains die existieren, aber LEERE Journeys haben:

1. **community** - Community Routes hinzufügen
2. **liveroom** - LiveRoom Routes hinzufügen
3. **marketplace** - Marketplace Routes hinzufügen
4. **gamification** - Gamification Routes hinzufügen
5. **billing** - Billing Routes hinzufügen
6. **notifications** - Notifications Routes hinzufügen
7. **storage** - Storage Routes hinzufügen
8. **system** - System Routes hinzufügen

---

### 5.3: Features implementieren

Features die existieren, aber LEER sind:

1. **collaboration/** (7 Sub-Features)
   - inverted_classroom
   - learning_journal
   - peer_instruction
   - peer_review
   - project_based_learning
   - project_portfolio
   - team_case

2. **exams/** (4 Sub-Features)
   - chapter_completion_system
   - comprehension_checker
   - ihk_exam_system
   - practical_exam_engine

3. **gamification/** (3 Sub-Features)
   - adaptive_difficulty
   - daily_recall
   - xp_quest_system

4. **interactive/whiteboard/** - Whiteboard Engine

5. **sandbox/** (3 Sub-Features)
   - code_sandbox
   - network_simulation
   - terminal_access

6. **tutor/** (2 Sub-Features)
   - npc_tutor
   - socratic_dialog

---

## Prioritäten-Reihenfolge

### PRIO 1: Kern-Domains (für Backend Start notwendig)

1. ✅ **auth** - Login/Register funktionieren muss
2. ✅ **users** - User Management
3. ✅ **health** - Health Checks
4. ✅ **i18n** - Übersetzungen (bereits in src/core/)

### PRIO 2: Content-Domains (bereits existieren, Routes erweitern)

5. ✅ **dashboard** - User Dashboard
6. ✅ **profile** - User Profile
7. ✅ **subscriptions** - Subscription Management
8. ✅ **tokens** - Token Wallet

### PRIO 3: Shared-Domains (neue Domains)

9. ✅ **organisations** - Organisations Management
10. ✅ **categories** - Category Hierarchies
11. ✅ **media** - Audio/TTS

### PRIO 4: AI-Domains (neue Domains)

12. ✅ **ai** - AI Operations
13. ✅ **agents** - Agent System
14. ✅ **prompts** - Prompt Management
15. ✅ **tutor** - AI Tutor (Domain, nicht Feature)

### PRIO 5: Journeys für Phase 4 Domains

16. ✅ **community** - Journeys
17. ✅ **liveroom** - Journeys
18. ✅ **gamification** - Journeys
19. ✅ **billing** - Journeys
20. ✅ **notifications** - Journeys
21. ✅ **storage** - Journeys
22. ✅ **system** - Journeys

### PRIO 6: System-Features (25 Features)

23-47. ✅ Alle Features in src/api/features/ implementieren

---

## Strategie

**Effizientes Vorgehen:**

1. **Phase 5.1** - Neue Domains erstellen (PRIO 1-4)
   - ai, agents, prompts, tutor (AI-Domains)
   - organisations, users, categories, media (Shared-Domains)
   - auth, health (Core-Domains)
   - dashboard, profile, subscriptions, tokens (User-Domains)

2. **Phase 5.2** - Journeys zu Phase 4 Domains (PRIO 5)
   - community, liveroom, gamification, billing, notifications, storage, system

3. **Phase 5.3** - System-Features (PRIO 6)
   - 25 Features implementieren

---

**Status:** Plan erstellt, ready to implement
**Nächster Schritt:** Phase 5.1 - Neue Domains erstellen
