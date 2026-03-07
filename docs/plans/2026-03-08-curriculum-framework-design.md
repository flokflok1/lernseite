# Design: Curriculum Framework Integration

**Datum:** 2026-03-08
**Status:** APPROVED
**Ziel:** Offizielle Rahmenpläne (IHK, Hochschule, Zertifizierungen) ins System integrieren. Prüfungsfragen den Rahmenplan-Positionen zuordnen. Lern-Kreislauf: Lernen → Prüfen → Schwächen erkennen → Gezielt nachlernen.

---

## Kontext

Das System hat bereits:
- **Exam Type Registry** (`exam_type_registry`) — IHK_FISI, IHK_FIAE, CompTIA etc.
- **Topic Taxonomy** (`exam_topic_taxonomy`) — frei definierte hierarchische Themen pro Exam-Typ
- **Exam Archive** — alte Prüfungsfragen mit Questions, Sessions, Regions
- **Intelligence Layer** — Schwächenprofile, Topic-Stats, Kurs-Generierung aus Prüfungsfragen
- **Exam Course Generator** — erstellt Kurse aus Prüfungsfragen gruppiert nach Topics
- **Exam Trainer** — zeitbasiertes Prüfungsüben mit Auswertung
- **AI Editor** — generiert Lerninhalte mit 12 Content-Lernmethoden

**Was fehlt:** Die Verbindung zum offiziellen Rahmenplan. Topics im System sind frei definiert, nicht an offizielle Berufsbildpositionen gebunden.

---

## Entscheidungen

| Frage | Entscheidung |
|-------|-------------|
| Scope | Generisch für alles (IHK, Hochschule, Zertifizierungen, Custom) |
| Import | AI-gestützter PDF-Import + manuelles Editing |
| Fragen-Mapping | AI schlägt vor, Admin bestätigt/korrigiert |
| Taxonomy-Relation | Ergänzen — Rahmenplan als obere Ebene, Topic Taxonomy als feinere Granularität darunter |

---

## Zwei Lernmodi

### AI Editor / Kurs-Generator → Lernen (ohne Zeitdruck)
- Generiert Kurse aus Rahmenplan-Positionen
- Nutzt die 12 Content-Lernmethoden (Deep Explanation, Flashcards, Drag & Drop etc.)
- User lernt die Themen in eigenem Tempo
- Kapitel = Rahmenplan-Position, Lessons = Lernziele mit verschiedenen LMs

### Exam Trainer → Prüfen (auf Zeit)
- Echte alte Prüfungsfragen unter Zeitdruck
- Simuliert Prüfungsbedingungen (z.B. 90 Min AP1, 90 Min AP2)
- Auswertung nach Rahmenplan-Positionen ("Position B.1: 60%, Position A.5: 30%")
- Schwächen fließen zurück in Kurs-Empfehlungen

### Kreislauf
```
Lernen (Kurs) → Prüfen (Exam Trainer) → Schwächen erkennen → Gezielt nachlernen → Wieder prüfen
```

---

## Datenmodell

Neue Tabellen im `assessments` Schema:

### `curriculum_frameworks`
Der Container für einen Rahmenplan.

| Spalte | Typ | Beschreibung |
|--------|-----|-------------|
| id | SERIAL PK | |
| name | VARCHAR(255) | z.B. "Ausbildungsrahmenplan Fachinformatiker 2020" |
| framework_type | VARCHAR(50) | ihk_ausbildung, hochschule, zertifizierung, custom |
| source_document | VARCHAR(500) | PDF-Pfad (optional) |
| version | VARCHAR(50) | z.B. "2020" |
| valid_from | DATE | Gültig ab |
| valid_until | DATE | Gültig bis (NULL = aktuell gültig) |
| metadata | JSONB | Zusätzliche Infos |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

### `curriculum_sections`
Abschnitte (z.B. A, B, C beim IHK-Rahmenplan).

| Spalte | Typ | Beschreibung |
|--------|-----|-------------|
| id | SERIAL PK | |
| framework_id | INT FK | → curriculum_frameworks |
| section_code | VARCHAR(10) | z.B. "A", "B", "C" |
| display_name | JSONB | {"de": "...", "en": "...", "pl": "..."} |
| description | JSONB | {"de": "...", "en": "...", "pl": "..."} |
| order_index | INT | Sortierung |
| applies_to | TEXT[] | Fachrichtungen z.B. ['FIAE','FISI'] oder NULL = alle |

### `curriculum_positions`
Berufsbildpositionen innerhalb eines Abschnitts.

| Spalte | Typ | Beschreibung |
|--------|-----|-------------|
| id | SERIAL PK | |
| section_id | INT FK | → curriculum_sections |
| position_number | VARCHAR(10) | z.B. "1", "2", "3" |
| display_name | JSONB | {"de": "...", "en": "...", "pl": "..."} |
| description | JSONB | {"de": "...", "en": "...", "pl": "..."} |
| order_index | INT | Sortierung |
| training_period | VARCHAR(20) | z.B. "1-18" oder "19-36" (Ausbildungsmonat) |

### `curriculum_objectives`
Einzelne Lernziele (a, b, c...) innerhalb einer Position.

| Spalte | Typ | Beschreibung |
|--------|-----|-------------|
| id | SERIAL PK | |
| position_id | INT FK | → curriculum_positions |
| objective_code | VARCHAR(10) | z.B. "a", "b", "c" |
| description | JSONB | {"de": "...", "en": "...", "pl": "..."} |
| order_index | INT | Sortierung |
| competency_level | VARCHAR(20) | kennen, anwenden, beherrschen (optional) |

### `curriculum_topic_mapping`
Verknüpfung: Rahmenplan-Objective ↔ Topic Taxonomy (strukturelles Mapping).

| Spalte | Typ | Beschreibung |
|--------|-----|-------------|
| id | SERIAL PK | |
| curriculum_objective_id | INT FK | → curriculum_objectives |
| topic_id | INT FK | → exam_topic_taxonomy |
| confidence | FLOAT | 0.0-1.0 (AI-generiert vs. manuell bestätigt) |
| mapped_by | VARCHAR(10) | 'ai' oder 'admin' |
| created_at | TIMESTAMPTZ | |

### `exam_question_curriculum_tags`
Verknüpfung: Prüfungsfrage ↔ Rahmenplan-Objective (inhaltliches Mapping).

| Spalte | Typ | Beschreibung |
|--------|-----|-------------|
| id | SERIAL PK | |
| question_id | INT FK | → exam_questions |
| curriculum_objective_id | INT FK | → curriculum_objectives |
| confidence | FLOAT | 0.0-1.0 |
| tagged_by | VARCHAR(10) | 'ai' oder 'admin' |
| created_at | TIMESTAMPTZ | |

### Verknüpfung zu Exam Types

`curriculum_frameworks` wird mit `exam_type_registry` verknüpft:

| Spalte | Tabelle | Beschreibung |
|--------|---------|-------------|
| framework_id | exam_type_registry (neue Spalte) | FK → curriculum_frameworks |

So weiß das System: Exam-Typ "IHK_FIAE" gehört zum Rahmenplan "Fachinformatiker 2020", Abschnitt B.

---

## AI-gestützter PDF-Import

### Flow

```
1. Admin lädt PDF hoch im Admin-Panel
2. Backend extrahiert Text (bestehender PDF-Extraktor aus archive_service)
3. AI analysiert Struktur → gibt JSON zurück
4. Admin sieht Preview als Tree-Ansicht
5. Admin korrigiert / bestätigt
6. System persistiert in die 4 Tabellen
```

### AI-Output Format

```json
{
  "name": "Ausbildungsrahmenplan Fachinformatiker 2020",
  "framework_type": "ihk_ausbildung",
  "sections": [
    {
      "code": "A",
      "name": {"de": "Berufsprofilgebende Fertigkeiten, Kenntnisse und Fähigkeiten"},
      "applies_to": ["FIAE", "FISI", "FIDP", "FIDN"],
      "positions": [
        {
          "number": "1",
          "name": {"de": "Planen, Vorbereiten und Durchführen von Arbeitsaufgaben"},
          "training_period": "1-36",
          "objectives": [
            {
              "code": "a",
              "description": {"de": "Auftragsunterlagen und Durchführbarkeit des Auftrages prüfen"}
            }
          ]
        }
      ]
    }
  ]
}
```

### Technisch

- Nutzt bestehenden `AIAdapter` mit Tool-Call Pattern
- Prompt bekommt extrahierten PDF-Text + Ausgabe-Schema
- Kein neuer AI-Aufruf-Pattern nötig

---

## AI-Auto-Mapping (Fragen → Curriculum)

### Batch-Mapping für bestehende Fragen

```
1. Admin klickt "Auto-Map to Curriculum" für einen Exam-Typ
2. System lädt alle Fragen ohne Curriculum-Tags
3. Für jede Frage (batched, z.B. 10er-Gruppen):
   - AI bekommt: Frage-Text + alle Curriculum-Objectives des Exam-Typs
   - AI gibt zurück: Top 1-3 passende Objectives mit Confidence
4. Ergebnisse als exam_question_curriculum_tags gespeichert
   (tagged_by='ai', confidence aus AI-Response)
5. Admin sieht Review-UI: Fragen mit AI-Vorschlägen
6. Admin bestätigt → confidence=1.0, tagged_by='admin'
   Admin korrigiert → neues Tag, altes gelöscht
```

### Inline-Mapping für neue Fragen

Beim Erstellen/Importieren einer Frage schlägt das System automatisch Curriculum-Positionen vor (gleicher AI-Call, einzeln statt batch).

---

## User-Facing Features

### Erweitertes Schwächenprofil

Bestehender `WeaknessProfile` wird um Rahmenplan-Dimension erweitert:

```
Statt:  "Schwach in: Netzwerke, SQL"
Jetzt:  "Schwach in:
         Rahmenplan Abschnitt A, Pos. 5: Qualitätssichernde Maßnahmen
           → speziell: Testverfahren (32% richtig)
         Rahmenplan Abschnitt B, Pos. 1: Softwareanwendungen
           → speziell: OOP (45%), Datenstrukturen (51%)"
```

### Prüfungsrelevanz-Gewichtung

Aus alten Prüfungen erkennt das System, welche Rahmenplan-Positionen häufig geprüft werden:

```
Position B.1 "Softwareanwendungen":  35% aller Fragen  ← Fokus!
Position A.3 "IT-Systeme bewerten":  20% aller Fragen
Position A.5 "Qualitätssicherung":   15% aller Fragen
```

Fließt in Kurs-Generierung und Exam Trainer ein — häufig geprüfte Positionen bekommen mehr Material.

### Kurs-Generierung nach Rahmenplan

Exam Course Generator kann Kurse nach Rahmenplan-Struktur generieren:
- Jedes Kapitel = eine Rahmenplan-Position
- Jede Lesson = ein Lernziel mit passender Lernmethode
- Gewichtung nach Prüfungsrelevanz

---

## Architektur (DDD)

| Layer | Neue Dateien |
|-------|-------------|
| **Infrastructure** | `repositories/exams/curriculum.py` — CRUD für alle 4 Curriculum-Tabellen + Mappings |
| **Application** | `services/exams/curriculum_service.py` — Import, AI-Mapping, Statistik-Aggregation |
| **API** | `api/v1/panel/admin/exams/curriculum.py` — Admin CRUD + Import + Auto-Map |
| **API** | `api/v1/panel/user/` — Erweiterung Schwächenprofil um Curriculum-Dimension |
| **Domain** | `domain/models/curriculum.py` — Value Objects (CurriculumFramework, CurriculumSection etc.) |
| **Frontend** | `panel/admin/assessment/curriculum/` — Admin-UI für Rahmenpläne |
| **Frontend** | Erweiterung ExamGoalsManager + ExamTrainer um Curriculum-Ansicht |

---

## Nicht im Scope (YAGNI)

- Automatische Erkennung welcher Rahmenplan zu einem User passt (User wählt explizit über Exam Goal)
- Rahmenplan-Versionierung (ein Framework = eine Version, bei neuer Version neuen Eintrag)
- Peer-to-Peer Curriculum-Sharing
- Integration mit externen LMS (Moodle etc.)
