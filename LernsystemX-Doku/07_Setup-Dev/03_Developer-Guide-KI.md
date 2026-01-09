# 35 – Developer-Guide KI (Version 4.0)

**Version:** 4.0
**Stand:** 2025-12-29
**Status:** Verbindlicher Guide für KI-gestützte Entwicklung
**Primary AI Engine:** Claude Opus 4.5 via Code CLI

---

## 0. Zweck dieses Dokuments

Dieses Dokument definiert, wie im LSX (LernSystemX) mit KI gearbeitet wird – für Developer, Creator, Admins und alle, die KI für Code, Konfiguration oder Inhalte nutzen.

**Ziel:** Standardisierter, sicherer und nachvollziehbarer Prozess:
- KI-Outputs passen **immer** zur LSX-Architektur
- Token-Budget effizient genutzt (180K pro Session)
- Multi-File-Refactors in einer Session
- Code, Konfiguration und Inhalte **sauber dokumentiert**
- Security, Performance und Qualität **systematisch** überprüft

---

## 1. Quality Gates G01–G10

Diese Ziele sind **verbindliche Quality Gates**.

| Ziel-ID | Ziel | Beschreibung | KI-Pflicht |
|---------|------|--------------|-----------|
| **G01** | Keine Duplikate | Keine `.old`, `.bak`, `_v2` Dateien | MUSS |
| **G02** | Konsistenz | KI folgt LSX-Architektur | MUSS |
| **G03** | Versionierung | Änderungen an CR/Task gebunden | MUSS |
| **G04** | Vollständigkeit | Keine Code-Fragmente | MUSS |
| **G05** | Dokumentation | Docstrings, Type Hints | MUSS |
| **G06** | Qualität | Tests für neue Features | MUSS |
| **G07** | Security | OWASP-konform, keine Secrets | MUSS |
| **G08** | Transparenz | KI erklärt Entscheidungen | MUSS |
| **G09** | Performance | Effiziente Queries, Caching | SOLLTE |
| **G10** | Accessibility | WCAG 2.1 AA | SOLLTE |

### Quick-Check

**KI (Self-Check):** "Prüfe gegen G01–G10 und liste auf, ob/wie sie eingehalten sind."

**Developer (Review):**
- [ ] G01 – Keine Duplikate
- [ ] G02 – Architektur konsistent
- [ ] G04 – Vollständige Dateien
- [ ] G05 – Docstrings vorhanden
- [ ] G06 – Tests dabei
- [ ] G07 – Keine Security-Risiken

---

## 2. Grundprinzipien

### 2.1 Dokumentations-First

KI muss **immer zuerst** die relevante Dokumentation kennen:
1. Developer beschreibt Task + nennt Dokumente
2. KI liest die Dateien direkt
3. KI wiederholt Constraints
4. Erst dann generiert KI Code

### 2.2 Keine Improvisation

**Verboten:**
- Neue Features ohne Spezifikation
- Eigene Architektur-Entscheidungen
- Ungefragt neue Dateien erstellen

**Erlaubt:**
- Code basierend auf Dokumentation
- Bugfixes mit Erklärung
- Optimierungen mit Begründung

### 2.3 Diff-First bei Änderungen

1. Bestehende Datei lesen
2. Geplante Änderung als Diff-Vorschau
3. Freigabe abwarten
4. Dann endgültigen Code liefern

### 2.4 Vollständige Outputs

KI liefert **immer vollständige Einheiten**:
- Ganze Dateien (nicht "Rest bleibt gleich")
- Vollständige SQL-Statements
- Vollständige Vue-Komponenten

---

## 3. Claude Opus 4.5 – Setup & Token-Management

### 3.1 Aktuelles Setup

| Aspekt | Details |
|--------|---------|
| **Modell** | Claude Opus 4.5 (via Code CLI) |
| **Context-Fenster** | 200K+ Tokens |
| **Stärken** | Multi-File-Refactors, Long-Context |

### 3.2 Token-Budget (180K Limit)

```
Systemaufruf + Constraints:     ~20K
Große Datei lesen:              ~30K
Analyse + Diff-Vorschlag:       ~20K
Code-Implementierung + Tests:   ~60K
Security/Performance-Review:    ~30K
Reserve:                        ~20K
─────────────────────────────────────
Total:                          ~180K
```

### 3.3 Prompt Caching

```bash
claude code --cache-min-tokens 2048 --model opus-4-5
```

### 3.4 Multi-Session-Strategie

**Session 1 – Analyse (150K):** Architektur-Plan erstellen
**Session 2 – Implementation (180K):** Code + Tests
**Session 3 – Review (100K):** Security, Performance

---

## 4. Start-Prompts

### 4.1 Globaler LSX Start-Prompt

```markdown
# LSX Developer Session – Claude Opus 4.5

Du arbeitest am **LSX LernSystemX**.

## Kontext
- 12 Content-Lernmethoden (LM00–LM11): `02_Lernmethoden.md`
- System-Features: `02a_System-Features.md`
- Kurs-Struktur: `37_Kurs-Lektions-Struktur.md`

## Quality Gates G01–G10 – VERBINDLICH

## Regeln
**Vor der Arbeit:**
1. Dokumentation lesen
2. Constraints wiederholen
3. Rückfragen wenn Info fehlt

**Während der Arbeit:**
4. Keine neuen Dateien ohne Anweisung
5. Änderungen: Diff-First
6. Nur vollständige Dateien
7. Type Hints (Python), Types (TS)

**Nach der Arbeit:**
8. Tests dabei
9. Doku aktualisieren
10. Breaking Changes kennzeichnen

Bereit: "✓ LSX Opus 4.5 Mode aktiv. Welche Aufgabe?"
```

### 4.2 Backend-Development

```markdown
# LSX Backend Developer Mode

**Fokus:** Python 3.12, Flask, psycopg3, PostgreSQL

**Relevante Docs:**
- 14_DB-Struktur.md
- 17_Backend-Struktur.md

**Rules:**
- DB-Zugriffe über Repository Pattern
- JWT Auth, Rollenmodell beachten
- Logging für sensitive Aktionen

Bereit: "✓ LSX Backend Mode."
```

### 4.3 Frontend-Development

```markdown
# LSX Frontend Developer Mode

**Fokus:** Vue.js 3 Composition API, Pinia, TailwindCSS

**Relevante Docs:**
- 16_Frontend-Struktur.md

**Rules:**
- Composition API (nicht Options API)
- TypeScript für Komponenten
- Responsive Design (Mobile First)

Bereit: "✓ LSX Frontend Mode."
```

---

## 5. Code-Templates

### 5.1 Python Backend

```python
# backend/app/api/[module].py
"""
[Module Description]
"""
from flask import Blueprint, request, jsonify
from typing import Dict, Optional
import logging

from app.repositories.[repo] import [Repo]Repository
from app.middleware.auth import require_auth, require_role

logger = logging.getLogger(__name__)

[module]_bp = Blueprint('[module]', __name__, url_prefix='/api/v1/[module]')


@[module]_bp.route('/<resource_id>', methods=['GET'])
@require_auth
def get_resource(resource_id: str) -> Dict:
    """
    Get single resource by ID.

    Args:
        resource_id: Resource identifier

    Returns:
        JSON representation of resource
    """
    try:
        resource = [Repo]Repository.find_by_id(resource_id)
        if not resource:
            return jsonify({'error': 'Not found'}), 404
        return jsonify(resource), 200
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': 'Internal error'}), 500
```

### 5.2 Vue.js Component

```vue
<!-- frontend/src/components/[ComponentName].vue -->
<template>
  <div class="[component-class]">
    <div v-if="loading">Loading...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else>
      <!-- Content -->
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * [Component Name]
 * [Description]
 */
import { ref, onMounted } from 'vue'

// Props
interface Props {
  resourceId?: string
}
const props = defineProps<Props>()

// State
const loading = ref(false)
const error = ref<string | null>(null)

// Methods
async function loadData() {
  loading.value = true
  try {
    // Load data
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Error'
  } finally {
    loading.value = false
  }
}

onMounted(() => loadData())
</script>
```

### 5.3 pytest Tests

```python
# backend/tests/test_[module].py
"""Tests for [module]"""
import pytest

class Test[Module]:
    """Test suite for [module]"""

    def test_get_success(self, client, auth_headers):
        """Test successful retrieval"""
        response = client.get('/api/v1/resource/123', headers=auth_headers)
        assert response.status_code == 200

    def test_get_not_found(self, client, auth_headers):
        """Test 404 for non-existent"""
        response = client.get('/api/v1/resource/99999', headers=auth_headers)
        assert response.status_code == 404

    def test_unauthorized(self, client):
        """Test without auth"""
        response = client.get('/api/v1/resource/123')
        assert response.status_code == 401
```

---

## 6. Internationalisierung (i18n)

### 6.1 i18n-Pflicht (KRITISCH)

**REGEL:** Alle sichtbaren Texte MÜSSEN über das i18n-System laufen. Hardcoded Strings sind verboten.

### 6.2 Unterstützte Sprachen

| Sprache | Code | Locale-Datei |
|---------|------|--------------|
| Deutsch | `de` | `frontend/src/locales/de.json` |
| English | `en` | `frontend/src/locales/en.json` |
| Polski | `pl` | `frontend/src/locales/pl.json` |

### 6.3 Workflow bei neuen Komponenten

```
1. Komponente erstellen
2. useI18n importieren
3. Alle Texte mit $t() / t() ersetzen
4. Keys in ALLE 3 Locale-Dateien hinzufügen
5. Build zur Validierung
```

### 6.4 Vue-Komponenten Pattern

```vue
<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

// In Script: t('key.path')
const errorMessage = t('common.unknownError')
</script>

<template>
  <!-- In Template: $t('key.path') -->
  <h1>{{ $t('admin.users.title') }}</h1>
  <p>{{ $t('errors.pageNotFoundDesc') }}</p>
</template>
```

### 6.5 Locale-Datei Struktur

```json
{
  "common": {
    "loading": "Laden...",
    "save": "Speichern",
    "cancel": "Abbrechen"
  },
  "admin": {
    "users": {
      "title": "Benutzerverwaltung",
      "subtitle": "Alle Benutzer im System"
    }
  }
}
```

### 6.6 Namenskonventionen für Keys

| Bereich | Prefix | Beispiel |
|---------|--------|----------|
| Allgemein | `common.*` | `common.save`, `common.loading` |
| Auth | `auth.*` | `auth.login`, `auth.password` |
| Navigation | `nav.*` | `nav.dashboard`, `nav.courses` |
| Admin-Seiten | `admin.[section].*` | `admin.users.title` |
| Fehler | `errors.*` | `errors.required`, `errors.network` |
| Kurse | `courses.*` | `courses.enrolled`, `courses.progress` |

### 6.7 Pluralisierung und Variablen

```vue
<!-- Mit Variablen -->
{{ $t('admin.roles.usersWithRole', { count: roleUsers.length }) }}

<!-- Locale-Datei -->
"usersWithRole": "Benutzer mit dieser Rolle ({count})"
```

### 6.8 Checkliste bei neuen Features

- [ ] `useI18n` import hinzugefügt
- [ ] `const { t } = useI18n()` im Script
- [ ] Alle hardcoded Strings ersetzt
- [ ] Keys in `de.json` hinzugefügt
- [ ] Keys in `en.json` hinzugefügt
- [ ] Keys in `pl.json` hinzugefügt
- [ ] Build erfolgreich (`npm run build`)

### 6.9 Häufige Fehler

| Fehler | Lösung |
|--------|--------|
| Key nicht gefunden | Key in allen 3 Locale-Dateien prüfen |
| Placeholder `{var}` wird nicht ersetzt | Parameter als zweites Argument übergeben |
| Build-Fehler mit i18n | Syntax in JSON-Dateien prüfen (Kommas!) |

---

## 7. Debugging-Workflow

### 7.1 Debug-Prompt-Template

```markdown
# Debug Request

## Error
[Vollständige Error Message]
[Stack Trace]

## Context
File: [Datei:Zeile]
Function: [Funktionsname]

## Code
```python
[Relevanter Code]
```

## Expected vs Actual
Expected: [Was sollte passieren]
Actual: [Was passiert]

## Request
1. Root Cause identifizieren
2. Mindestens 2 Lösungen
3. Code für Fix
4. Test für Fix
```

### 7.2 Häufige Fehlerklassen

**Database Errors:**
- IntegrityError → Foreign Key prüfen
- Connection Error → Pool-Settings prüfen

**Auth Errors:**
- 401 → JWT Token valid?
- 403 → User hat Rolle?

---

## 8. Security Audit Prompt

```markdown
# Security Audit

Prüfe auf OWASP Top 10:

## 1. Injection
- [ ] SQL Injection (parameterized queries)
- [ ] Command Injection

## 2. Authentication
- [ ] Passwörter gehasht (bcrypt)
- [ ] JWT korrekt validiert

## 3. Sensitive Data
- [ ] Keine Secrets in Code
- [ ] Keine Secrets in Logs

## 4. Access Control
- [ ] RBAC implementiert
- [ ] Row-Level Security

## 5. XSS
- [ ] Input Sanitization
- [ ] Output Encoding

Report: {severity, findings[], g07_status}
```

---

## 9. Performance Audit Prompt

```markdown
# Performance Audit

Prüfe:
- [ ] N+1 Query Problem
- [ ] Fehlende Indexes
- [ ] Caching-Möglichkeiten
- [ ] Große Payloads

Output:
{
  "queries": [{"sql": "...", "issue": "...", "fix": "..."}],
  "g09_status": "PASS|WARN"
}
```

---

## 10. Refactoring-Richtlinien

### 10.1 Dateien >500 Zeilen aufteilen

**Regel:** Keine Datei sollte >500 Zeilen haben.

**Wichtig:** Diese Regel hat **höchste Priorität** bei der Entwicklung. Bevor Code geschrieben wird:
1. Prüfen ob bestehende Dateien bereits groß sind
2. Bei neuen Features: Struktur planen
3. Komponenten von Anfang an modular aufbauen

**Strategie bei großen Dateien:**
1. Logische Blöcke identifizieren
2. In separate Module/Komponenten auslagern
3. Gemeinsame Logik in Composables/Services extrahieren
4. Imports anpassen
5. Tests anpassen

### 10.2 Vue.js Komponenten-Struktur (KRITISCH)

**WARNUNG:** Große Vue-Komponenten verursachen:
- Token-Limit-Probleme bei KI-Sessions (>25K Tokens)
- Schlechte Wartbarkeit
- Hohe Fehleranfälligkeit
- Schwierige Code-Reviews

**Limits:**
| Metrik | Maximum | Aktion bei Überschreitung |
|--------|---------|---------------------------|
| Zeilen pro Komponente | 500 | Sofort aufteilen |
| Template-Zeilen | 200 | UI in Sub-Komponenten |
| Script-Zeilen | 250 | Composables extrahieren |
| State-Variablen | 15 | In Stores oder Composables |

**Struktur für komplexe Features:**

```
components/feature/
├── FeatureMain.vue          # Orchestrierung (~200-300 Zeilen)
├── FeaturePanel.vue         # UI-Sektion (~150-250 Zeilen)
├── FeatureList.vue          # Liste (~100-200 Zeilen)
├── FeatureEditor.vue        # Editor (~150-250 Zeilen)
└── index.ts                 # Exports

composables/
├── useFeatureLogic.ts       # Shared State & Methods
└── useFeatureApi.ts         # API-Calls
```

**Beispiel: AI-Studio Refactoring (2025-12-29)**

```
ai-studio/                    # VORHER: 16.554 Zeilen in 14 Dateien
├── TutorTab.vue             # 3.698 → 141 Zeilen (-96%)
│   └── tutor/
│       ├── ChapterTheoryView.vue
│       └── LessonExplanationView.vue
├── KursBuilderTab.vue       # 2.945 Zeilen (Sub-Komponenten vorbereitet)
│   └── kurs-builder/
│       ├── ChatPanel.vue
│       ├── ConfirmationPanel.vue
│       ├── MaterialsPanel.vue
│       ├── StructurePanel.vue
│       ├── WorkflowPanel.vue
│       └── index.ts
├── ExamsTab.vue             # 1.830 Zeilen (Sub-Komponenten vorbereitet)
│   └── exams/
│       ├── ActivityPanel.vue
│       ├── ExamPreviewPanel.vue
│       ├── FilesPanel.vue
│       └── index.ts
└── GlobalSettingsTab.vue    # 1.342 Zeilen (Sub-Komponenten vorbereitet)
    └── global-settings/
        ├── ApiKeyModal.vue
        ├── ProfileEditor.vue
        ├── ProfileList.vue
        ├── ProviderGrid.vue
        └── index.ts
```

**Composables Pattern:**

```typescript
// composables/useFeature.ts
import { ref, computed, readonly } from 'vue'

export function useFeature() {
  // Private State
  const items = ref<Item[]>([])
  const isLoading = ref(false)

  // Public Read-Only State
  const itemCount = computed(() => items.value.length)

  // Methods
  async function loadItems() {
    isLoading.value = true
    try {
      items.value = await api.getItems()
    } finally {
      isLoading.value = false
    }
  }

  function reset() {
    items.value = []
  }

  // Expose readonly state + methods
  return {
    items: readonly(items),
    isLoading: readonly(isLoading),
    itemCount,
    loadItems,
    reset
  }
}
```

**Anti-Patterns zu vermeiden:**

| Anti-Pattern | Richtig |
|--------------|---------|
| Monolithische 3000+ Zeilen Komponente | Sub-Komponenten + Composables |
| 50+ State-Variablen in einer Komponente | Gruppieren in Composables |
| Duplizierte Logik zwischen Komponenten | Shared Composable erstellen |
| Alles in einer Datei | Unterordner mit index.ts |
| Inline-Styles >50 Zeilen | Separate CSS-Datei oder Tailwind |

### 10.3 Unterordner-Struktur

**Backend Admin Package (Refactored 2025-12-29):**

```
backend/app/api/admin/          # 40 endpoints, 7 modules
├── __init__.py                 # Imports all modules
├── courses.py      (329 LOC)   # Course CRUD (7 endpoints)
├── chapters.py     (200 LOC)   # Chapter management (5 endpoints)
├── lessons.py      (228 LOC)   # Lesson management (5 endpoints)
├── ai_jobs.py      (261 LOC)   # AI job management (4 endpoints)
├── exams.py        (318 LOC)   # Exam management (6 endpoints)
├── course_prompts.py (302 LOC) # Prompt overrides (6 endpoints)
└── course_files.py (346 LOC)   # File attachments (7 endpoints)
```

> Refactored from `admin_courses.py` (3624 LOC) → 7 modules (~2022 LOC total, -44%)

**Frontend Admin API Module (Refactored 2025-12-29):**

```
frontend/src/api/admin/         # 14 files
├── index.ts        (39 LOC)    # Re-exports all
├── types.ts       (1064 LOC)   # TypeScript interfaces
├── users.api.ts    (125 LOC)   # User management
├── organisations.api.ts (62 LOC)
├── courses.api.ts  (112 LOC)   # Course CRUD
├── chapters.api.ts (111 LOC)   # Chapter & Category
├── lessons.api.ts   (58 LOC)   # Lesson management
├── analytics.api.ts (144 LOC)  # System analytics
├── ai-jobs.api.ts   (43 LOC)   # AI job management
├── exams.api.ts     (73 LOC)   # Exam management
├── prompts.api.ts  (107 LOC)   # Course prompts
├── files.api.ts    (120 LOC)   # Course files
├── ai-models.api.ts (113 LOC)  # AI model management
├── learning-methods.api.ts (101 LOC)
└── lm-routing.api.ts (407 LOC) # LM model routing
```

> Refactored from `admin.api.ts` (3024 LOC) → 14 modules (~2679 LOC total, -11%)
>
> **Backward-compatible:** `admin.api.ts` re-exports from `admin/index.ts`

---

### 10.4 Dokumentations-Pflicht (KRITISCH)

> **WICHTIG:** Code und Dokumentation MÜSSEN synchron bleiben!

### Wann Dokumentation aktualisiert werden MUSS

| Aktion | Dokumentation aktualisieren |
|--------|----------------------------|
| Neue API-Endpoints erstellt | `17_Backend-Struktur.md`, `15_API-Spezifikation.md` |
| Neue Vue-Komponenten/Ordner | `16_Frontend-Struktur.md` |
| Neue Composables erstellt | `16_Frontend-Struktur.md` (Section 13) |
| Datenbank-Tabellen geändert | `14_DB-Struktur.md` |
| Lernmethoden geändert | `02_Lernmethoden.md`, `02a_System-Features.md` |
| KI-Prompts geändert | Prompt-Doku in `backend/app/ki/prompts/` |
| Rollen/Berechtigungen | `01_Rollenmodell.md`, `03_Zugriffssystem.md` |
| System-Architektur | `00_System-Übersicht.md` |

### Regel: Code-Struktur = Doku-Struktur

**Beispiel Backend:**
```
backend/app/api/
├── admin/                    # Muss in 17_Backend-Struktur.md
│   └── courses.py
├── admin_ai_studio.py        # Muss in 17_Backend-Struktur.md
└── admin_ai_tutor.py         # Muss in 17_Backend-Struktur.md
```

**Beispiel Frontend:**
```
frontend/src/components/desktop/windows/ai-studio/
├── /tutor/                   # Muss in 16_Frontend-Struktur.md
├── /kurs-builder/            # Muss in 16_Frontend-Struktur.md
└── TutorTab.vue              # Muss in 16_Frontend-Struktur.md
```

### Dokumentations-Checkliste bei Code-Änderungen

**Bei jedem Feature/Refactoring:**

- [ ] Ordner/Datei-Struktur in Doku aktualisiert
- [ ] API-Endpoints dokumentiert (wenn neu/geändert)
- [ ] Komponenten-Limits eingehalten (< 500 LOC)
- [ ] Sub-Komponenten in Doku aufgelistet
- [ ] Composables dokumentiert (wenn neu)

**Bei Backend-Änderungen:**
```bash
# Prüfen ob alle admin_*.py in Doku sind
ls backend/app/api/admin*.py
# Vergleichen mit 17_Backend-Struktur.md
```

**Bei Frontend-Änderungen:**
```bash
# Prüfen ob alle Unterordner in Doku sind
ls -d frontend/src/components/desktop/windows/ai-studio/*/
# Vergleichen mit 16_Frontend-Struktur.md
```

### Wer ist verantwortlich?

**Die KI (Claude) ist verantwortlich für:**
1. Erkennen wenn Doku-Updates nötig sind
2. Vorschlagen welche Dokumente aktualisiert werden müssen
3. Durchführen der Doku-Updates im gleichen Session

**Der User entscheidet:**
1. Ob Doku-Updates sofort oder später erfolgen
2. Welche zusätzlichen Details dokumentiert werden sollen

### Anti-Pattern: Code ohne Doku

| Anti-Pattern | Konsequenz |
|--------------|------------|
| Neue Ordner erstellen ohne Doku | Inkonsistenz, Verwirrung |
| API-Endpoints ohne Doku | Integration-Probleme |
| Refactoring ohne Doku-Update | Veraltete Doku, Fehler |
| Sub-Komponenten ohne Doku | Unbekannte Struktur |

**Richtig:**
```
1. Code schreiben/refactoren
2. Doku aktualisieren (gleiche Session!)
3. TypeScript-Check durchführen
4. Commit mit Code + Doku
```

---

## 11. Zusammenfassung

### Checkliste für jede Session

**Vor:**
- [ ] Start-Prompt geladen
- [ ] Relevante Dokumente identifiziert

**Während:**
- [ ] Dokumentation gelesen
- [ ] Diff-Vorschau für Änderungen
- [ ] Tests mitgeneriert

**Nach:**
- [ ] Code getestet
- [ ] Doku aktualisiert
- [ ] Version-Increment vorgeschlagen

### Anti-Patterns

| Anti-Pattern | Richtig |
|--------------|---------|
| "Mach mal" | Genaue Requirements |
| Code-Fragmente | Vollständige Dateien |
| Keine Tests | Tests immer dabei |
| Duplikate | Strikte Datei-Policy |

---

*Ende: 35 – Developer-Guide KI (Version 4.0)*
