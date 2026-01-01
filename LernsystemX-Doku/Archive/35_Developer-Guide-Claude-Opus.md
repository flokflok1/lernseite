# 35 – Developer-Guide KI-Prompts (Version 3.1 – Claude Opus 4.5 Code CLI)

**Version:** 3.1  
**Stand:** 2025-12-28  
**Status:** Verbindlicher Guide für KI-gestützte Entwicklung mit Claude Opus 4.5 (Code CLI)  
**Primary AI Engine:** Claude Opus 4.5 via Code CLI

---

## 0. Zweck dieses Dokuments

Dieses Dokument definiert, wie im LSX (LernSystemX) **mit Claude Opus 4.5 via Code CLI gearbeitet wird** – für Developer, Creator, Admins und alle, die KI für Code, Konfiguration oder Inhalte nutzen.

Ziel ist ein **standardisierter, sicherer und nachvollziehbarer Prozess**, bei dem:
- KI-Outputs **immer** zur LSX-Architektur passen,
- Token-Budget effizient genutzt wird (180K pro Session),
- Multi-File-Refactors in einer Session laufen,
- Code, Konfiguration und Inhalte **sauber dokumentiert** sind,
- Security, Performance und Qualität **systematisch** überprüft werden.

Dieses Dokument gilt **für alle KI-Sessions mit Claude Opus 4.5 Code CLI**.

---

## 1. Zentrale Ziele – Quality Gates G01–G10

Diese Ziele sind **verbindliche Quality Gates**.

- **KI muss sie einhalten** (Self-Check vor jedem Vorschlag).
- **Developer muss sie prüfen** (Review vor Merge/Übernahme).

### 1.1 Ziele-Tabelle G01–G10

| Ziel-ID | Ziel | Beschreibung | Erfolgskriterium | Messgröße | KI-Pflicht | Dev-Checklist |
|---------|------|--------------|------------------|-----------|-----------|---------------|
| **G01** | Keine Duplikate | Keine `.old`, `.bak`, `_v2`, `_final` Dateien oder Copy-Paste-Kopien | Sauberes Filesystem | Zusätzliche Dateien pro Change Request (CR) | MUSS | `git status` prüfen – nur explizit gewünschte neue Dateien |
| **G02** | Konsistenz | KI folgt LSX-Architektur (Backend-Factory, Blueprints, DB-Schema, Frontend-Struktur) | Code integriert sich reibungslos | Architektur-Verstöße pro Review | MUSS | Imports, Schichten, Namenskonventionen mit Doku abgleichen |
| **G03** | Versionierung | Änderungen sind immer an einen CR/Task gebunden | Nachvollziehbarkeit | Anzahl Änderungen ohne CR-Referenz | MUSS | Commit-/MR-Text enthält CR-ID / Ticket-Referenz |
| **G04** | Vollständigkeit | Keine Code-Fragmente („Rest bleibt gleich"), immer vollständige Dateien | Funktionaler Code | Anteil von Snippets ohne Kontext | MUSS | Kann der Code 1:1 ins Repo übernommen werden? |
| **G05** | Dokumentation | Docstrings, Type Hints, Kommentare, ggf. README/Doku-Update | Immer dokumentiert | Funktionen/Module ohne Docstring | MUSS | `grep -n "def "` vs. Docstrings abgleichen |
| **G06** | Qualität | Tests (Unit/Integration) für neue Features oder Bugfixes | Testbare Features | Test Coverage / neue Tests pro Feature | MUSS | `pytest` o.ä. ausführen, Tests für relevante Pfade vorhanden |
| **G07** | Security | OWASP-konformes Verhalten, Input-Validation, kein Hardcoding von Secrets | Keine kritischen Sicherheitslücken | Gefundene Security-Issues pro Review | MUSS | Bandit/ESLint-Security, Secret-Scan, SQL-Injection-Check |
| **G08** | Transparenz | KI erklärt Entscheidungen, verweist auf Doku, keine „magischen" Lösungen | Verständlicher Code | Unkommentierte komplexe Bereiche | MUSS | Begründungen im PR-Text / Kommentare vorhanden |
| **G09** | Performance | Effiziente Queries, Caching, keine unnötigen Schleifen, Nutzung von Indizes | Response-Zeiten im Zielbereich | Anzahl Slow-Queries / Performance-Regressionen | SOLLTE | `EXPLAIN ANALYZE`, Profiling, Monitoring-Hinweise |
| **G10** | Accessibility (A11y) | Frontend erfüllt relevante WCAG 2.1 AA-Aspekte | Barrierefreies UI | Anzahl A11y-Verstöße | SOLLTE | Screenreader, Kontrast, Tab-Navigation, `axe`-Checks |

### 1.2 Quick-Check für KI + Developer

Vor dem Akzeptieren eines KI-Vorschlags:

- **KI (Self-Check im Prompt):**
  - "Prüfe deinen Vorschlag explizit gegen G01–G10 und liste auf, ob/wie sie eingehalten sind."
- **Developer (Review):**
  - [ ] G01 – Keine Duplikate
  - [ ] G02 – Architektur konsistent zur Doku
  - [ ] G04 – Vollständige Dateien, kein Pseudocode
  - [ ] G05 – Docstrings & Type Hints vorhanden
  - [ ] G06 – Tests dabei/angepasst
  - [ ] G07 – Keine offensichtlichen Security-Risiken

---

## 2. Grundprinzipien der KI-Entwicklung

### 2.1 Dokumentations-First Approach

**Regel:** KI muss **immer zuerst** die relevante Dokumentation kennen, bevor Code oder Strukturvorschläge gemacht werden.

Ablauf (für Claude Opus 4.5):

1. Developer beschreibt Task + nennt relevante Dokumente (z.B. `02_Lernmethoden.md`, `02a_System-Features.md`, `14_DB-Struktur.md`).
2. KI liest die Dateien direkt (Code CLI mit `claude code`-Attach oder Copy-Paste).
3. KI rekonstruiert relevante Stellen und wiederholt Constraints.
4. Erst dann generiert KI Code oder Doku.
5. KI verweist auf genutzten Dokumentation.

### 2.2 Keine Improvisation

**Verboten:**
- Neue Features erfinden, die nicht in der Doku oder im CR beschrieben sind.
- Eigene Architektur-Entscheidungen, die dem C4-Modell, DB-Schema widersprechen.
- Ungefragt neue Dateien/Services/Endpoints anlegen.
- Von Dokumentation abweichen.

**Erlaubt:**
- Code auf Basis bestehender Spezifikation.
- Bugfixes mit klarer Begründung.
- Optimierungen (Performance/Security) mit Trade-off-Darstellung.
- Zusätzliche Tests und Doku.

### 2.3 Diff-First bei Änderungen

Bei Änderungen an bestehenden Dateien gilt immer:

1. **Bestehende Datei lesen.**
2. **Geplante Änderung als Diff-Vorschau beschreiben.**
3. Freigabe vom Developer abwarten.
4. **Dann** den endgültigen Code liefern.

### 2.4 Vollständige Outputs

KI liefert **immer vollständige, funktionsfähige Einheiten**:
- ganze Dateien (nicht "Rest bleibt gleich")
- vollständige SQL-Statements
- vollständige JSON-Schemata
- vollständige Vue-Komponenten

Bei sehr großen Dateien: KI beschreibt exakt, **welche Blöcke** ersetzt werden.

---

## 3. Claude Opus 4.5 – Setup, Context & Token-Management

### 3.1 Aktuelles KI-Setup

| Aspekt | Details |
|--------|---------|
| **Modell** | Claude Opus 4.5 (via Code CLI) |
| **Verwendung** | Backend, Frontend, LMs, System-Features, komplexe Refactorings, Doku |
| **Context-Fenster** | 200K+ Tokens |
| **Stärken** | Multi-File-Refactors, Long-Context-Analysen, Code-Konsistenz |
| **Limits** | Token-Budget pro Session begrenzt (siehe 3.2) |

### 3.2 Token-Budget pro Session (180K Limit)

Typische Verteilung für eine **komplexe Backend-Task**:

```
Systemaufruf + Constraints (dieses Dokument + LSX-Doku-Auszüge): ~20K
Große Datei (z.B. 14_DB-Struktur.md, courses.py): ~30K
Analyse + Diff-Vorschlag: ~20K
Vollständige Code-Implementierung + Tests: ~60K
Security/Performance-Review: ~30K
Reserve/Fehlerbehandlung: ~20K
─────────────────────────────────────────────────
Total: ~180K Tokens
```

**Strategie bei Budgetüberschuss:**
- Multi-Session-Approach nutzen (siehe 3.4).
- Große Dateien in Chunks/Ranges zerlegen.
- Wiederholte Doku mit Prompt Caching cachen (siehe 3.3).

### 3.3 Prompt Caching für wiederholte Inhalte

Claude Opus 4.5 unterstützt Prompt Caching. Nutze es für Dokumente, die in mehreren Sessions verwendet werden:

**Beispiel – LSX-Standard-Constraints cachen:**

```text
# System-Prompt (Cache-fähig – wird immer gleich verwendet)
- 19 Content-Lernmethoden (LM00–LM25)
- 9 Rollenmodell (Free, Premium, Creator, Teacher, etc.)
- LSX-Architektur: Factory Pattern, Flask Blueprints, PostgreSQL

# Reuse in den nächsten 5 Minuten: Cache Hit → spart ~20K Tokens
# Reuse nach 5 Minuten: Neuer Cache-Block, aber immer noch effizienter
```

**Code CLI mit Caching:**
```bash
claude code --cache-min-tokens 2048 --model opus-4-5
```

### 3.4 Multi-Session-Strategie

Für sehr große Tasks (z.B. kompletter Kurs-Refactor mit 15+ Dateien):

**Session 1 – Analyse & Design (Token Budget: 150K):**
- KI analysiert alle betroffenen Dateien
- Erstellt Architektur-Plan
- Listet alle Änderungen auf
- Output: CR-Beschreibung + Änderungsliste

**Session 2 – Implementation (Token Budget: 180K):**
- KI implementiert basierend auf Plan aus Session 1
- Nutzt Caching für wiederholte Doku
- Output: Vollständiger refactorierter Code + Tests

**Session 3 – Review & Optimierung (Token Budget: 100K):**
- KI führt Security-, Performance-, A11y-Checks durch
- Output: Optimierter Code, Ready-to-Merge

---

## 4. Code CLI – Workflows & Best Practices

### 4.1 Dateien mit Code CLI attachment

**Workflow für große Dateien:**

```bash
# Variante 1: Datei direkt attachment
claude code --attach "backend/api/courses.py" --model opus-4-5

# Variante 2: Verzeichnis mit Glob-Pattern
claude code --attach "backend/api/**/*.py" --model opus-4-5

# Variante 3: Dateibereich (für sehr große Dateien)
claude code --attach "backend/api/courses.py:1-500" --model opus-4-5
# Liest nur Zeilen 1–500, spart Tokens
```

**Best Practice:**
- Attachments für Doku (z.B. `02_Lernmethoden.md`, `14_DB-Struktur.md`).
- Copy-Paste für Code <10K Tokens.
- Datei-Ranges für Code >50K Tokens.

### 4.2 Structured Output aus Code CLI

Nutze JSON-Output für programmatische Verarbeitung:

```bash
claude code --model opus-4-5 --output-format json << 'EOF'
Analysiere die Datei courses.py und liste auf:
- Alle Funktionen mit Signatur
- Fehlende Docstrings
- Potenzielle Security-Risiken

Output als JSON: {"functions": [...], "missing_docs": [...], "security_risks": [...]}
EOF
```

### 4.3 Iterative Refinement (Session-Reuse)

Im Code CLI kannst du innerhalb einer Session iterieren:

```bash
claude code --model opus-4-5 << 'EOF'
# First Prompt
Schreibe einen Endpoint für Kurs-Erstellung mit Lernmethoden-Validierung.

# Second Prompt (in same session, spart Context-Reload)
Passe die Validierung an für System-Features wie TutorAgent.

# Third Prompt
Füge Tests für alle Edge-Cases hinzu.
```

**Vorteil:** Gesamter Context (alle bisherigen Prompts + Output) bleibt geladen → schneller & günstig.

---

## 5. LSX-spezifische Start-Prompts (Claude Opus 4.5)

### 5.1 Globaler LSX-Developer Start-Prompt

```markdown
# LSX Developer Session Start – Claude Opus 4.5

Du arbeitest am **LSX LernSystemX** – einem KI-gestützten, modularen Lernsystem mit 19 Content-Lernmethoden und separaten System-Features.

## Session Setup

- **Model:** Claude Opus 4.5 via Code CLI
- **Context Budget:** ~180K Tokens total (Reserve 20K)
- **Primary Attached Docs:** 02_Lernmethoden.md, 02a_System-Features.md, LernSystemX-Doku.md
- **Current Date:** 2025-12-28

## Kontext

- Content-Lernmethoden: `02_Lernmethoden.md` (19 LMs, LM00–LM25)
- System-Features: `02a_System-Features.md` (TutorAgent, Gamification, Learning Paths, etc.)
- Gesamtsystem: `LernSystemX-Doku.md` (Architektur, DB-Schema, Rollenmodell)

## Quality Gates (G01–G10) – VERBINDLICH

- G01: Keine Duplikate
- G02: Konsistenz mit LSX-Architektur
- G03: Versionierung über CR
- G04: Vollständige Outputs
- G05: Dokumentation (Docstrings, Type Hints)
- G06: Qualität (Tests)
- G07: Security (OWASP, keine Secrets)
- G08: Transparenz (Erklärungen)
- G09: Performance (Queries, Caching)
- G10: Accessibility (Frontend)

## Regeln

**Vor der Arbeit:**
1. Lese Dokumentation (attached oder zitiert).
2. Wiederhole Constraints kurz.
3. Stelle Rückfragen, wenn Info fehlt.

**Während der Arbeit:**
4. Keine neuen Dateien ohne explizite Anweisung.
5. Änderungen: Diff-First + Begründung.
6. Nur vollständige Dateien.
7. Type Hints (Python), saubere Typen (TS).
8. Error Handling + Logs.

**Nach der Arbeit:**
9. Tests dabei oder vorschlagen.
10. Doku + Docstrings aktualisieren.
11. Breaking Changes kennzeichnen.

## Token-Tracking

Aktuelle Token-Nutzung nach jeder Antwort kurz tracken:
- Geschätzte Tokens für Antwort
- Verbleibender Budget
- Wenn <30K Tokens übrig: Warnung geben

## Bereitschafts-Signal

Wenn ready: "✓ LSX Opus 4.5 Mode aktiv. Token Budget: 180K. Welche Aufgabe?"
```

### 5.2 Backend-Development (Python, Flask, PostgreSQL)

```markdown
# LSX Backend Developer Mode – Opus 4.5

**Fokus:**
- Python 3.12, Flask (Factory + Blueprints)
- PostgreSQL (psycopg3, JSONB)
- Celery, Redis

**Relevante Docs:**
- Backend-Architektur (LernSystemX-Doku.md)
- DB-Schema (14_DB-Struktur.md)
- KI-Pipeline (09_KI-Pipeline.md)

**Rules:**
- DB-Zugriffe über zentrale DB-Schicht
- JWT Auth, Rollenmodell strikt beachten
- Logging für sensitive Aktionen

**Bereit:** "✓ LSX Backend Mode. Token: 180K. Backend-Task?"
```

### 5.3 Lernmethoden & System-Features

```markdown
# LSX Lernmethoden / System-Features Mode – Opus 4.5

**Fokus:**
- 19 Content-Lernmethoden (LM00–LM25): `02_Lernmethoden.md`
- System-Features (TutorAgent, Gamification, etc.): `02a_System-Features.md`

**Rule:**
- Content-LMs = Aufgabenformate (individualisierbar)
- System-Features = Services um diese Formate herum

**Bereit:** "✓ LSX Learning Methods Mode. Token: 180K. Methode/Feature?"
```

---

## 6. Workflows mit Claude Opus 4.5 Code CLI

### 6.1 Neuer Endpunkt / neues Feature (Backend)

**Session 1 – Design & Review:**
1. Task + CR beschreiben
2. KI mit Backend-Start-Prompt starten
3. KI erstellt: Architektur + Request/Response Spec + DB-Schema-Änderungen
4. Developer reviewt Diff-Vorschau
5. Output: Approved Design Doc

**Session 2 – Implementation:**
1. Design aus Session 1 referenzieren
2. KI implementiert vollständen Code + Tests
3. Output: Production-ready Code

**Token-Budget:** ~150K Session 1 + ~180K Session 2 (mit Caching: ~150K)

### 6.2 Bugfix mit Claude

1. Bug reproduzieren (Testfall, Log-Output).
2. KI mit Logs + betroffene Dateien füttern.
3. KI analysiert (nur Analyse, kein Fix).
4. Developer gibt OK.
5. KI liefert Fix + Regressions-Tests.

**Token-Budget:** ~80–120K

### 6.3 Kompletter Kurs-Refactor (Multi-Session)

**Beispiel:** Alle 19 Content-LMs + 5 Kurs-Module refactoren.

**Session 1 – Analyse (Budget: 150K):**
- KI analysiert alle Dateien
- Listet notwendige Änderungen auf
- Erstellt Änderungsplan

**Session 2 – LMs anpassen (Budget: 180K, Caching aktiv):**
- KI passt alle 19 LM-Instances an
- Generiert neue Tests

**Session 3 – DB + API (Budget: 180K, Caching aktiv):**
- KI migriert DB-Schema
- Passt API-Endpoints an

**Gesamt:** ~510K Tokens (ohne Caching: ~660K)

---

## 7. Quality-Gate-Prompts (Claude Opus 4.5)

### 7.1 Security-Review

```markdown
# Security Audit – LSX Backend Code

Analysiere den folgenden Code auf OWASP Top 10:
- SQL-Injection, NoSQL-Injection
- Broken Auth, Broken Access Control
- Sensitive Data Exposure
- Hardcoded Secrets

Output-Format:
{
  "severity": "LOW|MEDIUM|HIGH",
  "findings": [{"issue": "...", "fix": "..."}],
  "g07_status": "PASS|FAIL"
}
```

### 7.2 Performance-Review

```markdown
# Performance Audit – LSX Query/Endpoint

Prüfe:
- EXPLAIN ANALYZE für alle Queries
- N+1-Queries, große Payloads
- Caching-Gelegenheiten

Output-Format:
{
  "queries": [{"sql": "...", "issue": "...", "optimization": "..."}],
  "g09_status": "PASS|WARN"
}
```

---

## 8. Fehlerbehandlung & Token-Exhaustion

### 8.1 Wenn Token-Budget überrannt wird

**Symptom:** KI sagt "Ich kann die Antwort nicht vollständig generieren wegen Token-Limit".

**Lösung:**
1. Task in kleinere Sub-Tasks zerlegen (siehe Multi-Session-Strategy).
2. Große Dateien in Ranges teilen (`--attach file.py:1-500`).
3. Prompt Caching aktivieren für wiederholte Inhalte.
4. Weniger Dokumentation attachen (nur essentielle Teile).

### 8.2 Bei Verletzung von G01–G10

Developer weist Antwort zurück mit Begründung:

```text
Verstoß gegen G01 und G05:
- G01: Du hast courses_old.py angelegt
- G05: 3 Funktionen ohne Docstrings

Bitte korrigieren und bestätige: "G01, G05 fixed".
```

KI re-generiert Code innerhalb gleicher Session (spart Context-Reload).

---

## 9. Zusammenfassung

- **Claude Opus 4.5 via Code CLI** ist die Primary KI-Engine für LSX.
- **Quality Gates G01–G10** sind verbindlich für alle Outputs.
- **Token-Budget:** 180K pro Session – Multi-Session-Strategy für große Tasks.
- **Prompt Caching** nutzen für Doku-Wiederverwendung (~20% Token-Ersparnis).
- **Code CLI Workflows** optimiert für Diff-First, Vollständigkeit, Multi-File-Refactors.

---

*Ende: 35 – Developer-Guide KI-Prompts (Version 3.1 – Claude Opus 4.5 Code CLI)*
