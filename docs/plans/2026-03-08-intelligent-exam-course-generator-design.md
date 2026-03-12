# Intelligent Exam Course Generator — Design

**Datum:** 2026-03-08
**Status:** APPROVED
**Ziel:** Exam Course Generator mit intelligenter Topic-Hierarchie, AI Editor Integration und Prüfungsmodus als einheitliches System

---

## Problem

1. **Duplikate:** Fragen mit mehreren Topics landen in mehreren Kapiteln (fix bereits deployed, aber Symptom eines tieferen Problems)
2. **Flache Topic-Liste:** 54 Topics ohne Hierarchie → 33 Kapitel statt sinnvoller 8-10 Oberkategorien
3. **Doppelte Content-Engine:** Course Generator hat eigene LM-Generierung parallel zum AI Editor → unterschiedliche Qualität, doppelter Code (G05)
4. **Starre Topic-Liste:** ANALYSIS_PROMPT hat 27 hartcodierte Topics, KI erfindet trotzdem eigene → inkonsistent
5. **Kein Prüfungskontext:** Generierte Kurse haben keinen Prüfungsmodus (Zeitlimit, Punkte, Simulation)

## Design-Entscheidungen

| Entscheidung | Gewählt | Alternativen verworfen |
|---|---|---|
| Topic-Hierarchie | Hybrid: DB-Taxonomie + KI-Fallback | Rein statisch; Rein KI-dynamisch |
| Content-Engine | AI Editor Pipeline (existierend) | Eigene Generator-Logik |
| Generierung | Hybrid: sofort Struktur + Celery-Batch | Nur interaktiv; Nur Batch |
| Kapitelstruktur | Aus `exam_topic_taxonomy` Hierarchie | Flache Topic-Liste |

---

## Architektur

### Ein System statt Zwei

```
VORHER (zwei getrennte Systeme):
  AI Editor ──→ Kurse ohne Prüfungsbezug
  Exam Course Generator ──→ Kurse mit eigener LM-Generierung

NACHHER (ein System):
  1. Taxonomie-Hierarchie → bestimmt Kapitelstruktur
  2. Exam Course Generator → plant Struktur (Kapitel, Fragen, LMs)
  3. AI Editor Pipeline → generiert Inhalte pro Kapitel (Batch via Celery)
  4. Prüfungsmodus → Flag auf Kurs (Zeitlimit, Punkte, Simulation)
```

### Drei Phasen

#### Phase A: Intelligente Taxonomie

**Einmaliger Bootstrap (für existierende Daten):**
- Alle 54 existierenden Topics aus `exam_questions` lesen
- Ein KI-Call pro `exam_type`: "Gruppiere diese Topics in 6-10 Oberkategorien"
- Ergebnis in `exam_topic_taxonomy` schreiben (parent_topic_id setzen)

**Bei jeder neuen Analyse (automatisch):**
- KI analysiert PDF wie bisher, darf beliebige Topics vergeben
- Neues Topic (nicht in Taxonomie)? → Einfügen mit `parent_topic_id = NULL`
- Classify-Call: "Zu welcher Oberkategorie gehört dieses Topic?"
- `parent_topic_id` setzen
- ANALYSIS_PROMPT wird dynamisch aus Taxonomie generiert (nicht mehr hartcodiert)

**Datenmodell (existiert bereits):**
```sql
assessments.exam_topic_taxonomy
├── topic_id (UUID, PK)
├── exam_type (FK → exam_type_registry)
├── topic_key (varchar, z.B. 'netzwerk')
├── topic_label (JSONB, i18n: {de: "Netzwerktechnik", en: "Networking"})
├── parent_topic_id (FK → self, NULL = Oberkategorie)
├── weight (numeric, Gewichtung)
└── created_at
```

**Curriculum-Integration:**
- Wenn `curriculum_topic_mapping` existiert → Hierarchie aus Rahmenplan ableiten
- Rahmenplan überschreibt KI-Vorschläge (höhere Autorität)

#### Phase B: Course Generator als Strukturplaner

**Preview-Flow (umgebaut):**
```
1. Fragen laden (wie bisher)
2. Topic-Hierarchie aus exam_topic_taxonomy lesen
3. Fragen nach parent_topic gruppieren:
   - Frage hat topic "subnetting" → parent = "netzwerk" → Kapitel "Netzwerktechnik"
   - Frage hat topic "kalkulation" → kein parent → eigenes Kapitel "Kalkulation"
4. Pro Kapitel: LMContentMapper bestimmt LM-Typen
5. ExamCoursePlan zurückgeben
```

**Generate-Flow (neu):**
```
1. preview() aufrufen → ExamCoursePlan
2. Kurs in DB erstellen (Struktur sofort verfügbar):
   - courses.courses mit exam_mode = true
   - courses.chapters pro Oberkategorie
   - Fragen-Referenzen pro Kapitel
3. Celery-Batch starten:
   - Pro Kapitel: AI Editor Pipeline triggern
   - Source → Theory → Lessons → Methods → Review → Finalize
   - Fortschritt in Redis tracken
4. Kurs-Status: "generating" → "ready" (wenn alle Kapitel fertig)
```

**User Experience:**
```
User klickt "Kurs generieren"
  → Kurs erscheint sofort im Editor (Struktur steht)
  → Fortschrittsanzeige: "12/8 Kapitel generiert"
  → User kann jederzeit:
      • Fertiges Kapitel öffnen und reviewen
      • Kapitel-Reihenfolge anpassen
      • Einzelnes Kapitel neu generieren lassen
      • Prüfungsfragen prüfen
  → Nach ~5-10 Min: Kurs komplett
```

#### Phase C: Prüfungsmodus

**Kurs-Flag statt eigener Kurs-Typ:**
```sql
-- Erweiterung courses.courses:
ALTER TABLE courses.courses ADD COLUMN exam_mode BOOLEAN DEFAULT FALSE;
ALTER TABLE courses.courses ADD COLUMN exam_config JSONB;

-- exam_config Beispiel:
{
  "time_limit_minutes": 90,
  "total_points": 100,
  "passing_percentage": 50,
  "simulation_exam_ids": ["uuid1", "uuid2"],
  "source_exam_type": "IHK_FISI_AP1",
  "source_region": "bw"
}
```

**Prüfungsmodus-Features:**
- Zeitlimit (Countdown)
- Punkteverteilung (original aus Prüfung)
- Prüfungssimulation (komplette Prüfung am Stück)
- Ergebnis-Auswertung (bestanden/nicht bestanden)
- Schwächen-Analyse pro Topic

---

## Betroffene Dateien

### Backend — Ändern

| Datei | Änderung |
|---|---|
| `application/services/exams/course_generator_service.py` | `_group_by_topic()` → Taxonomie-basiert |
| `application/services/exams/course_generator_builder.py` | AI Editor Pipeline statt eigene Generierung |
| `infrastructure/tasks/exam_archive_tasks.py` | Auto-Register neue Topics in Taxonomie |
| `infrastructure/tasks/exam_archive_tasks.py` | ANALYSIS_PROMPT dynamisch aus Taxonomie |
| `domain/models/exam_course_plan.py` | `ChapterPlan` um parent_topic erweitern |
| `domain/services/lm_content_mapper.py` | Unverändert (funktioniert bereits korrekt) |

### Backend — Neu

| Datei | Zweck |
|---|---|
| `application/services/exams/taxonomy_bootstrap_service.py` | Einmaliger KI-Bootstrap + Auto-Classify |
| `infrastructure/tasks/course_generation_tasks.py` | Celery-Tasks für Batch-Generierung |
| `api/v1/panel/admin/exams/taxonomy.py` | Admin-Endpoints für Taxonomie (CRUD) |

### Frontend — Ändern

| Datei | Änderung |
|---|---|
| `ExamCourseGenerator.vue` | Preview zeigt Oberkategorien statt flache Liste |
| `ExamCourseGenerator.vue` | "Generieren" öffnet Kurs im Editor mit Fortschritt |

### Datenbank

| Migration | Änderung |
|---|---|
| Neue Migration | `exam_mode` + `exam_config` auf `courses.courses` |

---

## Reihenfolge

1. **Taxonomie-Bootstrap** — befüllt `exam_topic_taxonomy` für existierende Daten
2. **Course Generator umbau** — nutzt Hierarchie statt flache Liste
3. **AI Editor Integration** — Celery-Batch statt eigene Generierung
4. **Prüfungsmodus** — exam_mode Flag + Zeitlimit/Punkte
5. **Admin-UI für Taxonomie** — Drag & Drop Editor (optional, später)

---

## Verifizierung

```bash
# 1. Taxonomie Bootstrap erfolgreich
psql -c "SELECT topic_key, parent_topic_id IS NOT NULL as has_parent
         FROM assessments.exam_topic_taxonomy
         WHERE exam_type = 'IHK_FISI_AP1';"

# 2. Preview zeigt 8-10 Kapitel statt 33
curl /api/v1/admin/exam-courses/preview?exam_type=IHK_FISI_AP1

# 3. Generierter Kurs hat exam_mode = true
# 4. AI Editor Inhalte pro Kapitel vorhanden
# 5. Frontend Build
cd frontend && npm run build
```
