# 38 - KI-Architektur-Konzept

> **Dokument-Version:** 1.0
> **Erstellt:** 2025-12-04
> **Status:** Konzept / Planung
> **Autor:** Pascal / Claude

---

## Übersicht

Dieses Dokument beschreibt die vollständige KI-Architektur für LernsystemX. Ziel ist ein **intelligentes, kosteneffizientes und qualitätsgesichertes System**, das:

- Verschiedene KI-Modelle optimal einsetzt
- Halluzinationen und Fehler minimiert
- Wissen aufbaut und wiederverwendet
- Kosten durch intelligentes Routing spart
- Administratoren volle Kontrolle gibt

---

## 1. Modell-Strategie

### 1.1 Verfügbare Modelle

| Anbieter | Modell | Stärken | Kosten | Einsatz |
|----------|--------|---------|--------|---------|
| **Anthropic** | Claude 3.5 Sonnet | Beste Qualität, lange Kontexte | $$$$ | Komplexe Erklärungen, Kurs-Erstellung |
| **Anthropic** | Claude 3 Haiku | Schnell, günstig | $ | Einfache Fragen, Chat |
| **OpenAI** | GPT-4o | Multimodal, schnell | $$$ | Bild-Analyse, Code |
| **OpenAI** | GPT-4 Turbo | Hohe Qualität | $$$ | Fallback für Claude |
| **OpenAI** | GPT-3.5 Turbo | Sehr günstig | $ | Simple Tasks |
| **OpenAI** | o1-preview | Reasoning | $$$$$ | Mathematik, Logik |
| **OpenAI** | text-embedding-ada-002 | Embeddings | ¢ | Semantische Suche |
| **Lokal** | Llama 3 / Mistral | Kostenlos | - | Optional: On-Premise |

### 1.2 Modell-Routing-Matrix

```
┌─────────────────────────────────────────────────────────────────────┐
│                      AUFGABE                                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  EINFACH                    MITTEL                    KOMPLEX       │
│  ────────                   ──────                    ───────       │
│                                                                      │
│  "Was ist HTTP?"      "Erkläre TCP/IP          "Erstelle einen      │
│  "Definition OSI"      mit Beispiel"            kompletten Kurs     │
│                                                  über Subnetting"   │
│       │                      │                         │            │
│       ▼                      ▼                         ▼            │
│  ┌─────────┐          ┌─────────────┐          ┌─────────────┐     │
│  │ Haiku   │          │ Sonnet      │          │ Sonnet +    │     │
│  │ GPT-3.5 │          │ GPT-4o      │          │ Review      │     │
│  │ ~$0.001 │          │ ~$0.01      │          │ ~$0.10      │     │
│  └─────────┘          └─────────────┘          └─────────────┘     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.3 Automatisches Routing

```python
class ModelRouter:
    """
    Wählt automatisch das beste Modell basierend auf:
    - Aufgaben-Komplexität
    - Kontext-Länge
    - Kosten-Budget
    - Qualitäts-Anforderung
    """

    def route(self, task: Task) -> Model:
        # Komplexität analysieren
        complexity = self.analyze_complexity(task)

        # Kontext-Länge prüfen
        context_tokens = self.count_tokens(task.context)

        if task.type == "embedding":
            return Models.ADA_002

        if task.type == "content_creation":
            return Models.CLAUDE_SONNET  # Immer beste Qualität

        if complexity == "simple" and context_tokens < 1000:
            return Models.CLAUDE_HAIKU  # Günstig & schnell

        if complexity == "medium":
            return Models.CLAUDE_SONNET

        if task.requires_reasoning:
            return Models.O1_PREVIEW  # Für Mathe/Logik

        return Models.CLAUDE_SONNET  # Default: Qualität
```

### 1.4 Modell-Konfiguration (Admin-UI)

```
┌─────────────────────────────────────────────────────────────────────┐
│  KI-MODELL VERWALTUNG                                    [Admin]    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Aktive Modelle:                                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ ☑ Claude 3.5 Sonnet    API-Key: sk-ant-***    ✓ Verbunden   │   │
│  │ ☑ Claude 3 Haiku       API-Key: sk-ant-***    ✓ Verbunden   │   │
│  │ ☑ GPT-4o               API-Key: sk-***        ✓ Verbunden   │   │
│  │ ☐ GPT-3.5 Turbo        API-Key: -             Deaktiviert   │   │
│  │ ☑ Ada Embeddings       API-Key: sk-***        ✓ Verbunden   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  Routing-Regeln:                                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Tutor-Chat:        Haiku (Primary) → Sonnet (Fallback)      │   │
│  │ Kurs-Erstellung:   Sonnet (Required)                        │   │
│  │ Embeddings:        Ada-002 (Required)                       │   │
│  │ Code-Generierung:  GPT-4o (Primary) → Sonnet (Fallback)     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  Kosten-Limits:                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Tages-Budget:      $50.00    [Heute: $12.34]                │   │
│  │ Monats-Budget:     $500.00   [Dieser Monat: $234.56]        │   │
│  │ Bei Überschreitung: ○ Warnen  ● Blockieren  ○ Downgrade    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Quality Control (Anti-Halluzination)

### 2.1 Das Problem

```
HALLUZINATION:
══════════════
Schüler: "Welchen Port verwendet DHCP?"
KI:       "DHCP verwendet Port 53"  ← FALSCH! (DNS ist 53, DHCP ist 67/68)

GEFAHR:
- Schüler lernt falsches Wissen
- Prüfung wird nicht bestanden
- Vertrauen in System sinkt
```

### 2.2 Mehrstufige Validierung

```
┌─────────────────────────────────────────────────────────────────────┐
│                    VALIDIERUNGS-PIPELINE                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  STUFE 1: GROUNDING (Verankerung im Kursmaterial)                   │
│  ═══════════════════════════════════════════════                    │
│                                                                      │
│  Frage: "Welchen Port nutzt DHCP?"                                  │
│                │                                                     │
│                ▼                                                     │
│  ┌─────────────────────────────────────┐                            │
│  │ Kursmaterial durchsuchen:           │                            │
│  │ → Lektion "DHCP Grundlagen"         │                            │
│  │ → Gefunden: "DHCP: UDP 67/68"       │                            │
│  └─────────────────────────────────────┘                            │
│                │                                                     │
│                ▼                                                     │
│  Prompt an KI:                                                      │
│  "Beantworte NUR basierend auf diesem Kontext:                      │
│   [Kursmaterial hier]                                               │
│   Frage: Welchen Port nutzt DHCP?"                                  │
│                                                                      │
│  ───────────────────────────────────────────────────────────────    │
│                                                                      │
│  STUFE 2: FAKTEN-CHECK                                              │
│  ═════════════════════                                              │
│                                                                      │
│  KI-Antwort: "DHCP nutzt UDP Port 67 (Server) und 68 (Client)"     │
│                │                                                     │
│                ▼                                                     │
│  ┌─────────────────────────────────────┐                            │
│  │ Fakten-Datenbank prüfen:            │                            │
│  │ → "DHCP" + "Port" = 67, 68 ✓        │                            │
│  │ → Confidence: 99%                   │                            │
│  └─────────────────────────────────────┘                            │
│                                                                      │
│  ───────────────────────────────────────────────────────────────    │
│                                                                      │
│  STUFE 3: UNSICHERHEITS-ERKENNUNG                                   │
│  ════════════════════════════════                                   │
│                                                                      │
│  KI-Antwort analysieren auf:                                        │
│  - "Ich glaube..." → Unsicher, Flag setzen                          │
│  - "Möglicherweise..." → Unsicher, Flag setzen                      │
│  - "Ich bin mir nicht sicher..." → An Mensch eskalieren             │
│                                                                      │
│  ───────────────────────────────────────────────────────────────    │
│                                                                      │
│  STUFE 4: FEEDBACK-LOOP                                             │
│  ══════════════════════                                             │
│                                                                      │
│  Schüler kann melden: "Das stimmt nicht!"                           │
│                │                                                     │
│                ▼                                                     │
│  ┌─────────────────────────────────────┐                            │
│  │ → Antwort wird markiert             │                            │
│  │ → Moderator prüft                   │                            │
│  │ → Korrektur in Wissensbasis         │                            │
│  │ → Alle zukünftigen Antworten fix    │                            │
│  └─────────────────────────────────────┘                            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.3 Confidence Scoring

```python
class AnswerValidator:
    """
    Bewertet die Zuverlässigkeit einer KI-Antwort
    """

    def validate(self, question: str, answer: str, context: str) -> ValidationResult:
        score = 1.0
        flags = []

        # 1. Ist die Antwort im Kontext verankert?
        if not self.is_grounded(answer, context):
            score -= 0.3
            flags.append("NOT_GROUNDED")

        # 2. Enthält unsichere Formulierungen?
        if self.has_uncertainty_phrases(answer):
            score -= 0.2
            flags.append("UNCERTAIN")

        # 3. Widerspricht Fakten-DB?
        if self.contradicts_facts(answer):
            score -= 0.5
            flags.append("FACT_CONFLICT")

        # 4. Wurde ähnliche Frage schon negativ bewertet?
        if self.has_negative_history(question):
            score -= 0.3
            flags.append("NEGATIVE_HISTORY")

        return ValidationResult(
            confidence=max(0, score),
            flags=flags,
            safe_to_show=score >= 0.7
        )
```

### 2.4 Eskalations-Stufen

| Confidence | Aktion |
|------------|--------|
| 90-100% | Direkt anzeigen |
| 70-89% | Anzeigen mit "Basierend auf Kursmaterial..." |
| 50-69% | Anzeigen mit Warnung + Feedback-Button |
| < 50% | Nicht anzeigen, an Dozent eskalieren |

---

## 3. Content-Pipeline (Kurs-Erstellung)

### 3.1 Wer erstellt was?

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CONTENT-ERSTELLUNG                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  MENSCHLICH ERSTELLT:              KI-UNTERSTÜTZT:                  │
│  ═══════════════════               ═══════════════                  │
│                                                                      │
│  • Kurs-Struktur                   • Theorie-Texte generieren       │
│  • Lernziele                       • Beispiele erstellen            │
│  • Quellenangaben                  • Übungen variieren              │
│  • Prüfungsfragen (Master)         • Erklärungen umformulieren      │
│  • Faktische Inhalte prüfen        • Zusammenfassungen              │
│  • Freigabe erteilen               • Übersetzungen                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Erstellungs-Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    KURS-ERSTELLUNGS-PIPELINE                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. CREATOR GIBT INPUT                                              │
│     ════════════════════                                            │
│     - Thema: "DHCP für CCNA"                                        │
│     - Lernziele: "Schüler versteht DORA-Prozess"                    │
│     - Quelldokumente hochladen (PDFs, Skripte)                      │
│     - Schwierigkeitsgrad: Mittel                                    │
│                                                                      │
│                          │                                          │
│                          ▼                                          │
│                                                                      │
│  2. KI GENERIERT ENTWURF                                            │
│     ══════════════════════                                          │
│     ┌────────────────────────────────────────┐                      │
│     │ Claude Sonnet analysiert:              │                      │
│     │ → Quelldokumente                       │                      │
│     │ → Bestehende Kurse als Referenz        │                      │
│     │ → Lernziel-Anforderungen               │                      │
│     │                                        │                      │
│     │ Generiert:                             │                      │
│     │ → Kapitel-Struktur                     │                      │
│     │ → Theorie-Texte                        │                      │
│     │ → Beispiele                            │                      │
│     │ → Übungsfragen (Vorschläge)            │                      │
│     └────────────────────────────────────────┘                      │
│                                                                      │
│                          │                                          │
│                          ▼                                          │
│                                                                      │
│  3. AUTOMATISCHE PRÜFUNG                                            │
│     ════════════════════                                            │
│     ┌────────────────────────────────────────┐                      │
│     │ ☑ Plagiat-Check (gegen alle Kurse)     │                      │
│     │ ☑ Fakten-Validierung                   │                      │
│     │ ☑ Vollständigkeit (alle Lernziele?)    │                      │
│     │ ☑ Sprach-Qualität                      │                      │
│     │ ☑ Schwierigkeitsgrad-Konsistenz        │                      │
│     └────────────────────────────────────────┘                      │
│                                                                      │
│                          │                                          │
│                          ▼                                          │
│                                                                      │
│  4. CREATOR REVIEW                                                  │
│     ══════════════════                                              │
│     - Inhalte prüfen und anpassen                                   │
│     - Fehler korrigieren                                            │
│     - Eigene Beispiele hinzufügen                                   │
│     - "Zur Freigabe einreichen"                                     │
│                                                                      │
│                          │                                          │
│                          ▼                                          │
│                                                                      │
│  5. MODERATOR FREIGABE                                              │
│     ════════════════════                                            │
│     ┌────────────────────────────────────────┐                      │
│     │ Moderator prüft:                       │                      │
│     │ → Qualitäts-Mindeststandards           │                      │
│     │ → Keine falschen Informationen         │                      │
│     │ → Keine Copyright-Verletzungen         │                      │
│     │ → Angemessene Sprache                  │                      │
│     │                                        │                      │
│     │ ✓ Freigeben  ✗ Ablehnen (mit Grund)   │                      │
│     └────────────────────────────────────────┘                      │
│                                                                      │
│                          │                                          │
│                          ▼                                          │
│                                                                      │
│  6. VERÖFFENTLICHUNG                                                │
│     ════════════════════                                            │
│     - Kurs ist live                                                 │
│     - Tutor-Wissen wird indexiert                                   │
│     - Embeddings werden erstellt                                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.3 Qualitäts-Metriken für Kurse

| Metrik | Beschreibung | Mindest-Wert |
|--------|--------------|--------------|
| **Vollständigkeit** | Alle Lernziele abgedeckt? | 100% |
| **Lesbarkeit** | Flesch-Reading-Score | > 60 |
| **Fakten-Score** | Validierte Aussagen | > 95% |
| **Plagiat-Score** | Originalität | > 85% |
| **Übungs-Ratio** | Übungen pro Theorie-Seite | > 0.5 |

---

## 4. Tutor-System (Live-Antworten)

### 4.1 Architektur

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TUTOR-SYSTEM ARCHITEKTUR                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  FRONTEND                                                           │
│  ════════                                                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                                                               │  │
│  │    Lerninhalt                           ┌─────────────────┐  │  │
│  │    [Theorie / Übung]                    │  🤖 Tutor       │  │  │
│  │                                         │  ─────────────  │  │  │
│  │                                         │  "Ich kann dir  │  │  │
│  │                                         │   helfen!"      │  │  │
│  │                                         │                 │  │  │
│  │                                         │  [Frage stellen]│  │  │
│  │                                         └─────────────────┘  │  │
│  │                                                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              │ WebSocket                            │
│                              ▼                                      │
│  BACKEND                                                            │
│  ═══════                                                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                                                               │  │
│  │   TutorService                                                │  │
│  │   ┌─────────────────────────────────────────────────────┐    │  │
│  │   │                                                      │    │  │
│  │   │  1. Kontext sammeln                                  │    │  │
│  │   │     → Aktueller Kurs, Lektion                        │    │  │
│  │   │     → User-History (was hat er falsch gemacht?)      │    │  │
│  │   │     → User-Level                                     │    │  │
│  │   │                                                      │    │  │
│  │   │  2. Wissens-Pyramide durchsuchen                     │    │  │
│  │   │     → Level 1: Statischer Content (kostenlos)        │    │  │
│  │   │     → Level 2: Gelerntes Wissen (kostenlos)          │    │  │
│  │   │     → Level 3: KI-API (wenn nötig)                   │    │  │
│  │   │                                                      │    │  │
│  │   │  3. Antwort validieren                               │    │  │
│  │   │     → Grounding, Fakten-Check                        │    │  │
│  │   │                                                      │    │  │
│  │   │  4. Antwort zurückgeben                              │    │  │
│  │   │     → Streaming für lange Antworten                  │    │  │
│  │   │                                                      │    │  │
│  │   └─────────────────────────────────────────────────────┘    │  │
│  │                                                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 Tutor-Persönlichkeiten

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TUTOR-KONFIGURATION (Admin)                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Verfügbare Tutoren:                                                │
│                                                                      │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐           │
│  │ 🎓 Professor  │  │ 🤝 Buddy      │  │ 🏆 Coach      │           │
│  │ ───────────── │  │ ───────────── │  │ ───────────── │           │
│  │ Formal        │  │ Locker        │  │ Motivierend   │           │
│  │ Detailliert   │  │ Einfach       │  │ Fordernd      │           │
│  │ Akademisch    │  │ Mit Humor     │  │ Zielorientiert│           │
│  └───────────────┘  └───────────────┘  └───────────────┘           │
│                                                                      │
│  Anpassungen:                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Name:             [Lernhelfer Max                        ]   │   │
│  │ Avatar:           [🤖 Roboter ▼]                            │   │
│  │ Sprache:          [Deutsch ▼] [Du-Form ○ Sie-Form ●]       │   │
│  │ Ausführlichkeit:  [Kurz ○ ● Mittel ○ Ausführlich]          │   │
│  │ Proaktivität:     [────●──────] 60%                         │   │
│  │                   (Wie oft ungefragt Hilfe anbieten)        │   │
│  │ Max. Antwortlänge:[500] Wörter                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.3 Tutor-Modi

| Modus | Trigger | Verhalten |
|-------|---------|-----------|
| **Passiv** | Standard | Avatar sichtbar, wartet auf Interaktion |
| **Proaktiv** | Schüler macht 3x Fehler, lange Pause | Bietet Hilfe an |
| **Aktiv** | Schüler fragt | Beantwortet Fragen |
| **Lehr-Modus** | Vor neuer Übung | Erklärt erst die Theorie |
| **Review-Modus** | Nach Übung | Erklärt was falsch war |

---

## 5. Wissens-Management

### 5.1 Wissens-Hierarchie

```
┌─────────────────────────────────────────────────────────────────────┐
│                    WISSENS-HIERARCHIE                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  EBENE 3: KI-API (Fallback)                                         │
│  ══════════════════════════                                         │
│  → Nur wenn Ebene 1+2 keine Antwort haben                           │
│  → Antwort wird in Ebene 2 gespeichert!                             │
│  → Kosten: $0.01 - $0.10 pro Frage                                  │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                         KI-API                               │   │
│  │              Claude Sonnet / GPT-4o                          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ▲                                      │
│                              │ Nur wenn nötig                       │
│  ════════════════════════════════════════════════════════════════  │
│                                                                      │
│  EBENE 2: Gelerntes Wissen (Cache)                                  │
│  ═════════════════════════════════                                  │
│  → Aus früheren Fragen gespeichert                                  │
│  → Semantisches Matching (Embeddings)                               │
│  → Kosten: ~$0.0001 (nur Embedding-Vergleich)                       │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  tutor_knowledge (Datenbank)                                 │   │
│  │  ┌─────────────────────────────────────────────────────┐    │   │
│  │  │ Frage: "Was ist DHCP?"                              │    │   │
│  │  │ Antwort: "DHCP ist ein Protokoll..."                │    │   │
│  │  │ Embedding: [0.82, 0.1, ...]                         │    │   │
│  │  │ Usage: 1,234 mal verwendet                          │    │   │
│  │  │ Quality: 98%                                        │    │   │
│  │  └─────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ▲                                      │
│                              │ Semantische Suche                    │
│  ════════════════════════════════════════════════════════════════  │
│                                                                      │
│  EBENE 1: Statischer Content (Kursmaterial)                         │
│  ══════════════════════════════════════════                         │
│  → Vom Creator erstellt                                             │
│  → Definitionen, Theorie, Beispiele                                 │
│  → Kosten: $0 (bereits vorhanden)                                   │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Kurs: CCNA Netzwerk                                         │   │
│  │  ├── Lektion 1: DHCP Grundlagen                              │   │
│  │  │   └── "DHCP (Dynamic Host Configuration Protocol)..."     │   │
│  │  ├── Lektion 2: DORA-Prozess                                 │   │
│  │  │   └── "Discover, Offer, Request, Acknowledge..."          │   │
│  │  └── ...                                                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.2 Wissens-Trennung (Multi-Tenancy)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    WISSENS-ISOLATION                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│                    GLOBALES WISSEN                                  │
│                    (Alle dürfen nutzen)                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  → Allgemeine IT-Konzepte                                    │   │
│  │  → Öffentliche Standards (TCP/IP, HTTP, etc.)                │   │
│  │  → Community-geteiltes Wissen                                │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│          ┌───────────────────┼───────────────────┐                 │
│          ▼                   ▼                   ▼                 │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐           │
│  │ ORGANISATION │   │ ORGANISATION │   │ ORGANISATION │           │
│  │ A (Firma)    │   │ B (Schule)   │   │ C (Creator)  │           │
│  ├──────────────┤   ├──────────────┤   ├──────────────┤           │
│  │ Privates     │   │ Privates     │   │ Privates     │           │
│  │ Wissen:      │   │ Wissen:      │   │ Wissen:      │           │
│  │              │   │              │   │              │           │
│  │ • Interne    │   │ • Schul-     │   │ • Eigene     │           │
│  │   Prozesse   │   │   spezifisch │   │   Kurse      │           │
│  │ • Firmen-    │   │ • Klassen-   │   │ • Notizen    │           │
│  │   Richtlinien│   │   material   │   │              │           │
│  │ • Nur für    │   │ • Nur für    │   │ • Nur für    │           │
│  │   Mitarbeiter│   │   Schüler    │   │   Creator    │           │
│  └──────────────┘   └──────────────┘   └──────────────┘           │
│         ✗                  ✗                  ✗                    │
│    Nicht sichtbar für andere Organisationen!                       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.3 Wissens-Zuweisung (Admin)

```
┌─────────────────────────────────────────────────────────────────────┐
│  WISSENS-BEREICHE VERWALTEN                              [Admin]    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Wissens-Pools:                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Pool              │ Einträge │ Zugriff        │ Aktionen    │   │
│  ├───────────────────┼──────────┼────────────────┼─────────────┤   │
│  │ 🌍 Global         │ 12,345   │ Alle           │ [Ansehen]   │   │
│  │ 🏢 Firma XYZ      │ 234      │ Nur Org        │ [Bearbeiten]│   │
│  │ 🎓 Schule ABC     │ 567      │ Nur Org        │ [Bearbeiten]│   │
│  │ 📚 Kurs: CCNA     │ 89       │ Kurs-Teilnehmer│ [Bearbeiten]│   │
│  │ 📚 Kurs: Python   │ 156      │ Kurs-Teilnehmer│ [Bearbeiten]│   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  Tutor-Wissens-Zuweisung:                                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Tutor "Netzwerk-Experte" darf zugreifen auf:                │   │
│  │                                                              │   │
│  │ ☑ 🌍 Globales Wissen                                        │   │
│  │ ☑ 📚 Kurs: CCNA                                             │   │
│  │ ☑ 📚 Kurs: CompTIA Network+                                 │   │
│  │ ☐ 📚 Kurs: Python Basics (nicht relevant)                   │   │
│  │ ☐ 🏢 Firma XYZ (kein Zugriff)                               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 6. Admin-Verwaltung (UI-Konzept)

### 6.1 KI-Dashboard

```
┌─────────────────────────────────────────────────────────────────────┐
│  KI-SYSTEM DASHBOARD                                     [Admin]    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐       │
│  │ API-Kosten      │ │ Anfragen heute  │ │ Cache-Hitrate   │       │
│  │ Heute           │ │                 │ │                 │       │
│  │ $12.34          │ │ 4,567           │ │ 78%             │       │
│  │ ↓ 15% vs gestern│ │ ↑ 8% vs gestern │ │ ↑ 5% vs gestern │       │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘       │
│                                                                      │
│  Kosten-Verlauf (letzte 30 Tage):                                   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │    $                                                         │   │
│  │ 50 ┤                                                         │   │
│  │ 40 ┤      ╭─╮                                                │   │
│  │ 30 ┤   ╭──╯ ╰──╮    ╭─╮                                     │   │
│  │ 20 ┤╭──╯        ╰────╯ ╰──╮                                 │   │
│  │ 10 ┤                       ╰────────────────                │   │
│  │  0 └─────────────────────────────────────────                │   │
│  │    1. Dez                              30. Dez               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  Modell-Nutzung:                                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Claude Sonnet   ████████████████████████████████  68% $8.40 │   │
│  │ Claude Haiku    ████████████                      24% $0.80 │   │
│  │ GPT-4o          ████                               6% $2.10 │   │
│  │ Ada Embeddings  ██                                 2% $1.04 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  Top-Fragen (diese Woche):                                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 1. "Was ist der Unterschied zwischen TCP und UDP?" (234x)   │   │
│  │ 2. "Erkläre Subnetting" (189x)                              │   │
│  │ 3. "Wie funktioniert DHCP?" (145x)                          │   │
│  │ 4. "Was ist eine Variable?" (132x)                          │   │
│  │ 5. "Erkläre SQL Joins" (98x)                                │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.2 Navigation

```
KI-Verwaltung
├── Dashboard (Übersicht, Kosten, Nutzung)
├── Modelle
│   ├── Konfiguration (API-Keys, Limits)
│   ├── Routing-Regeln
│   └── Fallback-Ketten
├── Tutoren
│   ├── Tutor-Liste (CRUD)
│   ├── Persönlichkeiten
│   └── Wissens-Zuweisung
├── Wissens-Basis
│   ├── Einträge durchsuchen
│   ├── Import/Export
│   ├── Qualitäts-Review
│   └── Duplikat-Bereinigung
├── Quality Control
│   ├── Gemeldete Fehler
│   ├── Review-Queue
│   └── Fakten-Datenbank
└── Analytics
    ├── Fragen-Statistik
    ├── Kosten-Analyse
    └── Cache-Performance
```

---

## 7. Kosten-Optimierung

### 7.1 Kosten-Reduktions-Strategien

```
┌─────────────────────────────────────────────────────────────────────┐
│                    KOSTEN-OPTIMIERUNG                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  STRATEGIE 1: Semantisches Caching                                  │
│  ══════════════════════════════════                                 │
│                                                                      │
│  "Was ist DHCP?"         ─┐                                         │
│  "Erklär mir DHCP"        ├─→ Similarity > 90% → EINE Antwort      │
│  "Wie funktioniert DHCP?" ─┘      aus Cache (kostenlos)             │
│                                                                      │
│  Ersparnis: ~70% der Fragen sind Variationen                        │
│                                                                      │
│  ───────────────────────────────────────────────────────────────    │
│                                                                      │
│  STRATEGIE 2: Modell-Downgrade                                      │
│  ══════════════════════════════                                     │
│                                                                      │
│  Einfache Frage? → Haiku ($0.001) statt Sonnet ($0.01)              │
│                                                                      │
│  Ersparnis: ~90% pro einfache Frage                                 │
│                                                                      │
│  ───────────────────────────────────────────────────────────────    │
│                                                                      │
│  STRATEGIE 3: Kontext-Kompression                                   │
│  ═══════════════════════════════                                    │
│                                                                      │
│  Statt: Ganzes Kursmaterial (50,000 Tokens)                         │
│  Nur:   Relevante Absätze (2,000 Tokens)                            │
│                                                                      │
│  Ersparnis: ~96% Input-Tokens                                       │
│                                                                      │
│  ───────────────────────────────────────────────────────────────    │
│                                                                      │
│  STRATEGIE 4: Batch-Processing                                      │
│  ═════════════════════════════                                      │
│                                                                      │
│  Nachts: Häufige Fragen vorberechnen                                │
│  Mit Anthropic Batch API: 50% Rabatt                                │
│                                                                      │
│  Ersparnis: 50% für Batch-geeignete Inhalte                         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 7.2 ROI-Projektion

| Zeitraum | Monatl. Kosten | Mit Optimierung | Ersparnis |
|----------|---------------|-----------------|-----------|
| Monat 1 | $500 | $500 | 0% |
| Monat 3 | $800 | $600 | 25% |
| Monat 6 | $1,200 | $600 | 50% |
| Monat 12 | $2,000 | $500 | 75% |
| Monat 24 | $3,000 | $300 | 90% |

**Break-Even:** Nach ~6 Monaten zahlt sich die Wissens-Basis aus.

---

## 8. Datenbank-Schema

### 8.1 Neue Tabellen

```sql
-- ================================================================
-- KI-MODELL-KONFIGURATION
-- ================================================================

CREATE TABLE ki_models (
    model_id SERIAL PRIMARY KEY,
    provider VARCHAR(50) NOT NULL,          -- 'anthropic', 'openai'
    model_name VARCHAR(100) NOT NULL,       -- 'claude-3-5-sonnet'
    display_name VARCHAR(100),              -- 'Claude 3.5 Sonnet'

    -- Konfiguration
    api_key_encrypted TEXT,                 -- Verschlüsselter API-Key
    is_active BOOLEAN DEFAULT TRUE,

    -- Kosten
    input_cost_per_1k DECIMAL(10,6),        -- $ pro 1000 Input-Tokens
    output_cost_per_1k DECIMAL(10,6),       -- $ pro 1000 Output-Tokens

    -- Limits
    max_tokens INT DEFAULT 4096,
    context_window INT DEFAULT 128000,

    -- Fähigkeiten
    supports_vision BOOLEAN DEFAULT FALSE,
    supports_function_calling BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ================================================================
-- TUTOR-KONFIGURATION
-- ================================================================

CREATE TABLE tutors (
    tutor_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE,

    -- Persönlichkeit
    avatar VARCHAR(10),                     -- Emoji
    personality VARCHAR(50),                -- 'professor', 'buddy', 'coach'
    language VARCHAR(5) DEFAULT 'de',
    formality VARCHAR(20) DEFAULT 'formal', -- 'formal', 'informal'

    -- Verhalten
    proactivity_level INT DEFAULT 50,       -- 0-100
    max_response_length INT DEFAULT 500,    -- Wörter

    -- System-Prompt
    system_prompt TEXT,

    -- Modell-Zuweisung
    primary_model_id INT REFERENCES ki_models(model_id),
    fallback_model_id INT REFERENCES ki_models(model_id),

    -- Wissens-Zugriff
    knowledge_scope JSONB DEFAULT '{"global": true}',

    -- Zuordnung
    organisation_id UUID REFERENCES organisations(organisation_id),
    category_ids INT[],                     -- Nur diese Kategorien

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ================================================================
-- WISSENS-BASIS (Gelerntes Wissen)
-- ================================================================

CREATE TABLE tutor_knowledge (
    knowledge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Semantische Suche
    question_text TEXT NOT NULL,
    question_embedding VECTOR(1536),        -- OpenAI Ada Embedding

    -- Antwort
    answer_text TEXT NOT NULL,
    answer_variations JSONB,                -- Verschiedene Formulierungen

    -- Kontext
    category_id INT REFERENCES course_categories(category_id),
    course_id UUID REFERENCES courses(course_id),
    language VARCHAR(5) DEFAULT 'de',

    -- Qualität
    quality_score FLOAT DEFAULT 0.5,        -- 0-1
    usage_count INT DEFAULT 0,
    positive_feedback INT DEFAULT 0,
    negative_feedback INT DEFAULT 0,

    -- Zugriffsrechte
    scope VARCHAR(20) DEFAULT 'global',     -- 'global', 'organisation', 'course'
    organisation_id UUID REFERENCES organisations(organisation_id),

    -- Metadaten
    source VARCHAR(50),                     -- 'user_question', 'import', 'generated'
    created_by UUID REFERENCES users(user_id),
    reviewed_by UUID REFERENCES users(user_id),
    reviewed_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP,

    -- Deduplizierung
    content_hash VARCHAR(64) UNIQUE
);

-- Index für Vektor-Suche (pgvector)
CREATE INDEX idx_knowledge_embedding ON tutor_knowledge
USING ivfflat (question_embedding vector_cosine_ops)
WITH (lists = 100);

-- ================================================================
-- FAKTEN-DATENBANK (Validierung)
-- ================================================================

CREATE TABLE verified_facts (
    fact_id SERIAL PRIMARY KEY,

    topic VARCHAR(200) NOT NULL,            -- 'DHCP Port'
    fact_text TEXT NOT NULL,                -- 'DHCP nutzt UDP 67/68'

    -- Kategorisierung
    category_id INT REFERENCES course_categories(category_id),
    tags TEXT[],

    -- Quelle
    source_type VARCHAR(50),                -- 'rfc', 'cisco_doc', 'textbook'
    source_url TEXT,

    -- Status
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by UUID REFERENCES users(user_id),
    verified_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW()
);

-- ================================================================
-- FEEDBACK & QUALITÄTSKONTROLLE
-- ================================================================

CREATE TABLE ki_feedback (
    feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Kontext
    knowledge_id UUID REFERENCES tutor_knowledge(knowledge_id),
    user_id UUID REFERENCES users(user_id),

    -- Feedback
    rating INT CHECK (rating BETWEEN -1 AND 1), -- -1=schlecht, 0=neutral, 1=gut
    feedback_text TEXT,
    reported_issue VARCHAR(50),             -- 'wrong', 'unclear', 'incomplete'

    -- Bearbeitung
    status VARCHAR(20) DEFAULT 'pending',   -- 'pending', 'reviewed', 'fixed'
    reviewed_by UUID REFERENCES users(user_id),
    reviewed_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW()
);

-- ================================================================
-- API-NUTZUNG & KOSTEN
-- ================================================================

CREATE TABLE ki_usage_log (
    usage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Request
    model_id INT REFERENCES ki_models(model_id),
    tutor_id INT REFERENCES tutors(tutor_id),
    user_id UUID REFERENCES users(user_id),

    -- Tokens
    input_tokens INT,
    output_tokens INT,

    -- Kosten
    cost_usd DECIMAL(10,6),

    -- Cache
    cache_hit BOOLEAN DEFAULT FALSE,

    -- Timing
    latency_ms INT,

    created_at TIMESTAMP DEFAULT NOW()
);

-- Tägliche Aggregation für Dashboard
CREATE TABLE ki_usage_daily (
    date DATE PRIMARY KEY,

    total_requests INT DEFAULT 0,
    cache_hits INT DEFAULT 0,

    total_input_tokens BIGINT DEFAULT 0,
    total_output_tokens BIGINT DEFAULT 0,

    total_cost_usd DECIMAL(10,2) DEFAULT 0,

    -- Pro Modell
    model_breakdown JSONB
);
```

---

## 9. Implementierungs-Reihenfolge

### Phase 2.1: Basis-Infrastruktur
1. ☐ Datenbank-Migrationen (ki_models, tutors, tutor_knowledge)
2. ☐ KI-Modell-Service (Multi-Provider-Support)
3. ☐ API-Key-Verwaltung (verschlüsselt)
4. ☐ Kosten-Tracking

### Phase 2.2: Wissens-System
1. ☐ pgvector Extension installieren
2. ☐ Embedding-Service (Ada-002)
3. ☐ Semantische Such-Funktion
4. ☐ Wissens-Cache-Logik

### Phase 2.3: Tutor-Core
1. ☐ Tutor-Service (Fragen beantworten)
2. ☐ Kontext-Builder (Kurs, User, History)
3. ☐ Prompt-Templates
4. ☐ Antwort-Validierung

### Phase 2.4: Frontend
1. ☐ Tutor-Widget (Vue Component)
2. ☐ WebSocket-Integration
3. ☐ Chat-UI
4. ☐ Admin-Dashboard

### Phase 2.5: Quality & Optimierung
1. ☐ Feedback-System
2. ☐ Fakten-Validierung
3. ☐ Auto-Modell-Routing
4. ☐ Batch-Processing

---

## 10. Offene Fragen

| # | Frage | Optionen | Entscheidung |
|---|-------|----------|--------------|
| 1 | Wo werden API-Keys gespeichert? | ENV / DB (verschlüsselt) / Vault | Offen |
| 2 | pgvector oder externe Vektor-DB? | pgvector / Pinecone / Weaviate | Offen |
| 3 | Wer darf Tutoren erstellen? | Nur Admin / Org-Admins / Creator | Offen |
| 4 | Globales Wissen editierbar? | Nur Admin / Moderatoren | Offen |
| 5 | Kosten-Limits pro User? | Ja (wie viel?) / Nein | Offen |

---

## Changelog

| Version | Datum | Änderungen |
|---------|-------|------------|
| 1.0 | 2025-12-04 | Initiales Konzept erstellt |
